#!/usr/bin/env python3
"""
Consult - CLI Entry Point

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.
"""

import asyncio
import argparse
import logging
import sys
import time

from src.workflows import ConsensusWorkflow
from src.config import Config
from src.core.exceptions import (
    MissingAPIKeyError,
    InvalidProviderError,
    AgentResponseError,
    AgentTimeoutError,
    FeatureGatedError,
)
from src.core.license import (
    get_license_manager,
    get_current_tier,
    get_current_limits,
    Tier,
)
from src.core.rate_limiter import (
    get_rate_limiter,
    check_can_query,
    record_query,
)
from src.core.paths import ensure_consult_structure, get_logs_dir
from src.core.security import get_contextual_logger, set_session_context
from src.core.identity import get_user_id, generate_session_id
from src.core.feature_gate import (
    check_feature,
    check_limit,
    require_team_mode,
    require_sessions,
    require_attachments,
    require_export,
    require_custom_experts,
)


def _setup_logging() -> logging.Logger:
    """Initialize contextual logging with user/session IDs.

    Every log line will include [u:USER_ID s:SESSION_ID] for easy filtering.
    """
    # Get license key to derive user ID
    license_key = get_license_manager().get_license_key()
    user_id = get_user_id(license_key) if license_key else "anonymous"
    session_id = generate_session_id()

    # Set session context for all loggers
    set_session_context(user_id=user_id, session_id=session_id)

    # Create contextual logger
    log_file = get_logs_dir() / "consult.log"
    logger = get_contextual_logger("consult", log_file=str(log_file))
    return logger


def _check_tier_access(args) -> tuple[bool, str]:
    """Check if current tier allows the requested features.

    Uses centralized feature_gate module for consistent messaging and logging.

    Returns:
        Tuple of (allowed, error_message)
    """
    try:
        # Check team mode access
        if args.mode == "team":
            require_team_mode()

        # Check session/memory access
        if args.memory_session:
            require_sessions()

        # Check attachment access
        if args.attachments:
            require_attachments()

        # Check markdown export access
        if args.markdown:
            require_export()

        # Check max iterations limit
        check_limit("max_iterations", args.max_iterations)

        # Check custom experts
        if args.experts != "default":
            # Allow built-in expert sets for free tier
            from src.agents.expert_manager import ExpertManager
            if args.experts not in ExpertManager.EXPERT_SETS:
                require_custom_experts()

        return True, ""

    except FeatureGatedError as e:
        return False, e.user_message()


def _check_quota() -> tuple[bool, str]:
    """Check if user has remaining quota.

    Returns:
        Tuple of (allowed, error_message)
    """
    can_query, error = check_can_query()
    if not can_query:
        tier = get_current_tier()
        limits = get_current_limits()
        return False, (
            f"{error}\n"
            f"Current tier: {tier.value} ({limits.queries_per_day} queries/day, {limits.queries_per_hour}/hour)\n"
            f"Upgrade at: https://getconsult.dev/pricing"
        )
    return True, ""


def _print_quota_status():
    """Print current quota status."""
    rate_limiter = get_rate_limiter()
    warning = rate_limiter.show_quota_warning()
    if warning:
        print(f"Note: {warning}")


def _validate_and_prepare_config(args):
    """Validate configuration and prepare environment"""
    if not Config.validate_config(mode=args.mode, provider=args.provider):
        if args.mode == "team":
            available = Config.get_team_providers()
            print("Team mode requires at least 2 API keys. Please check your .env file.")
            print(f"Available providers: {', '.join(available)}")
            print("Required: At least 2 of ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY")
        else:
            target_provider = args.provider or Config.DEFAULT_SINGLE_PROVIDER
            print(f"Missing API key for {target_provider}. Please check your .env file.")
            available = Config.get_available_providers()
            if available:
                print(f"Available providers: {', '.join(available)}")
                print(f"Try: --provider {available[0]}")
        return False
    return True


def _create_workflow(args, memory_manager):
    """Create and configure the consensus workflow"""
    workflow = ConsensusWorkflow(
        max_iterations=args.max_iterations,
        consensus_threshold=args.consensus_threshold,
        mode=args.mode,
        provider=args.provider,
        expert_config=args.experts,
        memory_manager=memory_manager,
    )
    if args.mode == "team":
        available_teams = Config.get_team_providers()
        workflow_name = f"Team Competition ({', '.join([t.title() for t in available_teams])})"
    else:
        provider_name = (args.provider or Config.DEFAULT_SINGLE_PROVIDER).title()
        workflow_name = f"Single Provider ({provider_name})"

    return workflow, workflow_name


def _print_engine_info(args):
    """Print engine/model information"""
    if args.mode == "team":
        available_teams = Config.get_team_providers()
        engines = []
        for provider in available_teams:
            model_id = Config.get_model_for_provider(provider)
            engines.append(model_id)
        print(f"Mode: Team Competition ({' vs '.join(engines)})")
    else:
        provider_name = args.provider or Config.DEFAULT_SINGLE_PROVIDER
        model_id = Config.get_model_for_provider(provider_name)
        print(f"Engine: {model_id}")
    print()


def _print_consensus_explanation():
    """Print detailed explanation of how the consensus mechanism works."""
    print("""
HOW CONSENSUS WORKS IN CONSULT

WHAT IS CONSENSUS?
Consensus is NOT "how similar are expert solutions?" - that would be meaningless.
Instead, we measure EXPLICIT CROSS-EXPERT APPROVAL.

Each expert reviews each OTHER expert's solution and answers:
  "Would I sign off on THIS going to production?"


THE PROCESS
For 3 experts (A, B, C), we collect 6 pairwise approvals:

  Expert A reviews -> Expert B's solution: APPROVE
  Expert A reviews -> Expert C's solution: CONCERNS
  Expert B reviews -> Expert A's solution: APPROVE
  Expert B reviews -> Expert C's solution: OBJECT
  Expert C reviews -> Expert A's solution: APPROVE
  Expert C reviews -> Expert B's solution: APPROVE

  Aggregate approval = average of all scores


VERDICTS
| Verdict              | Score | Meaning                                      |
|----------------------|-------|----------------------------------------------|
| APPROVE              | 1.0   | I would sign off on this for production      |
| APPROVE_WITH_CONCERNS| 0.7   | Acceptable, but these issues should be noted |
| OBJECT               | 0.0   | Cannot endorse - fundamental problems exist  |


WHAT GETS EVALUATED (Weighted by Production Impact)
| Dimension         | Weight | Why This Weight?                            |
|-------------------|--------|---------------------------------------------|
| Requirements      | 30%    | Solving wrong problem = everything wasted   |
| Approach/Tech     | 25%    | Wrong foundation = hard to fix later        |
| Trade-offs        | 20%    | Bad trade-offs = real engineering failures  |
| Architecture      | 15%    | Poor design = long-term technical debt      |
| Implementation    | 10%    | Can't build it = worthless design           |


OUTCOMES
Approval >= threshold (default 80%)
  -> Consensus reached -> Proceed to final synthesis

Approval < threshold AND iterations remaining
  -> Another refinement cycle (experts see objections, refine solutions)

Approval < threshold AND max iterations reached
  -> Orchestrator intervention (proposes middle-ground resolution)
""")


async def async_main():
    """Async entry point for CLI"""
    # Initialize secure logging (writes to ~/.consult/logs/)
    logger = _setup_logging()
    logger.info("Consult CLI started")

    parser = argparse.ArgumentParser(
        description="Consult - Expert Panel Consensus System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  consult -p "Design a chat app database"
  consult -p "Build secure API" --experts security_focused
  consult -p "ML pipeline design" --experts ai_system --mode team
  consult --list-experts
        """.strip(),
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version and exit"
    )
    parser.add_argument(
        "--status", "-s", action="store_true", help="Show license tier and quota status, then exit"
    )
    parser.add_argument(
        "--problem", "-p", help="Problem statement to solve (required unless --list-experts)"
    )
    parser.add_argument("--max-iterations", "-i", type=int, default=1, help="Max consensus iterations")
    parser.add_argument(
        "--consensus-threshold", "-t", type=float, default=0.8, help="Consensus threshold (0.0-1.0)"
    )

    # Team mode and provider selection
    parser.add_argument(
        "--mode",
        "-m",
        choices=["single", "team"],
        default="single",
        help="Mode: single (one provider) or team (multiple providers competing)",
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "google"],
        help="Single provider to use (default: anthropic). Only used in single mode.",
    )

    # Expert configuration
    parser.add_argument(
        "--experts",
        "-e",
        default="default",
        help="Expert configuration: expert set name ('security_focused', 'ai_system') or comma-separated names",
    )
    parser.add_argument(
        "--list-experts",
        action="store_true",
        help="Show all available expert types and sets, then exit",
    )
    parser.add_argument(
        "--explain-consensus",
        action="store_true",
        help="Explain how the consensus mechanism works, then exit",
    )

    # Markdown output option
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Save output to Markdown file (useful for large team mode outputs)",
    )
    parser.add_argument(
        "--markdown-filename",
        help="Custom filename for markdown output (enables appending for follow-ups)",
    )

    # Memory session for continuity
    parser.add_argument(
        "--memory-session", help="Path to memory session file for conversation continuity"
    )

    # Attachment support
    parser.add_argument(
        "--attachments",
        "-a",
        nargs="*",
        help="Paths to image/PDF files to include in the analysis",
    )

    # Dry run for CI/testing
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and workflow setup without making API calls",
    )

    args = parser.parse_args()

    # Handle version command
    if args.version:
        from src import __version__
        print(f"Consult v{__version__}")
        return

    # Handle status command
    if args.status:
        ensure_consult_structure()
        tier = get_current_tier()
        limits = get_current_limits()
        rate_limiter = get_rate_limiter()
        status = rate_limiter.check_quota()

        print("Consult Status")
        print("=" * 40)
        print(f"\nTier: {tier.value}")
        print(f"\nLimits:")
        print(f"  Queries/day:    {limits.queries_per_day}")
        print(f"  Queries/hour:   {limits.queries_per_hour}")
        print(f"  Max iterations: {limits.max_iterations}")
        print(f"  Max experts:    {limits.max_experts}")
        print(f"\nFeatures:")
        print(f"  Team mode:    {'✓' if limits.team_mode else '✗'}")
        print(f"  TUI:          {'✓' if limits.tui_enabled else '✗'}")
        print(f"  Sessions:     {'✓' if limits.sessions_enabled else '✗'}")
        print(f"  Attachments:  {'✓' if limits.attachments_enabled else '✗'}")
        print(f"  Export:       {'✓' if limits.export_enabled else '✗'}")
        print(f"  Custom experts: {'✓' if limits.custom_experts else '✗'}")
        print(f"\nUsage Today:")
        print(f"  Used:      {status.queries_today}")
        print(f"  Remaining: {status.remaining_today}")
        print(f"  This hour: {status.remaining_this_hour}")
        print(f"\nUpgrade at: https://getconsult.dev/pricing")
        return

    # Handle list experts command
    if args.list_experts:
        from src.agents.expert_manager import ExpertManager

        ExpertManager.print_available_configurations()
        return

    # Handle explain consensus command
    if args.explain_consensus:
        _print_consensus_explanation()
        return

    # Handle dry-run mode
    if args.dry_run:
        print("Consult Dry Run")
        print("=" * 40)

        # Check directory structure
        ensure_consult_structure()
        print("✓ Directory structure OK (~/.consult/)")

        # Check tier/license
        tier = get_current_tier()
        limits = get_current_limits()
        print(f"✓ License validation OK (tier: {tier.value})")

        # Check quota system
        rate_limiter = get_rate_limiter()
        status = rate_limiter.check_quota()
        print(f"✓ Quota system OK ({status.remaining_today} queries remaining)")

        # Check provider configuration
        available = Config.get_available_providers()
        if available:
            print(f"✓ API keys configured: {', '.join(available)}")
        else:
            print("⚠ No API keys configured (set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY)")

        # Check workflow imports
        try:
            from src.workflows import ConsensusWorkflow
            from src.agents.expert_manager import ExpertManager
            from src.memory.memory_persistence import MemoryPersistence
            print("✓ Workflow modules OK")
        except ImportError as e:
            print(f"✗ Import error: {e}")
            sys.exit(1)

        # Check expert configurations
        from src.agents.expert_manager import ExpertManager
        expert_sets = ExpertManager.list_expert_sets()
        print(f"✓ Expert sets OK ({len(expert_sets)} sets available)")

        # Validate a workflow can be created (without running)
        if available:
            provider = available[0]
            try:
                workflow = ConsensusWorkflow(
                    max_iterations=1,
                    consensus_threshold=0.8,
                    mode="single",
                    provider=provider,
                    expert_config="default",
                    memory_manager=None,
                )
                print(f"✓ Workflow initialization OK (provider: {provider})")
                # Clean up (we're already in async context)
                await workflow.close()
            except Exception as e:
                print(f"✗ Workflow initialization failed: {e}")
                sys.exit(1)
        else:
            print("⚠ Skipping workflow initialization (no API keys)")

        print("\n" + "=" * 40)
        print("Dry run complete. All checks passed.")
        return

    # Validate that problem is provided for normal operation
    if not args.problem:
        parser.error("--problem/-p is required (unless using --list-experts, --status, or --dry-run)")

    # Ensure Consult home directory exists
    ensure_consult_structure()

    # Check tier access for requested features
    tier_ok, tier_error = _check_tier_access(args)
    if not tier_ok:
        print(f"Feature not available:\n{tier_error}")
        return

    # Check quota before running
    quota_ok, quota_error = _check_quota()
    if not quota_ok:
        print(f"Query limit reached:\n{quota_error}")
        return

    # Print any quota warnings
    _print_quota_status()

    # Validate configuration
    if not _validate_and_prepare_config(args):
        return

    # Setup memory manager and persistence
    memory_persistence = None
    memory_manager = None
    if args.memory_session:
        from src.memory.memory_persistence import MemoryPersistence

        memory_persistence = MemoryPersistence(args.memory_session)
        memory_persistence.load_state()
        memory_manager = memory_persistence.memory_manager
        if memory_persistence.memory_manager.final_solution:
            print("Continuing conversation with memory context")
        else:
            print("Starting new conversation")

    # Create workflow
    workflow, workflow_name = _create_workflow(args, memory_manager)

    # Print engine info
    print("Consult")
    _print_engine_info(args)

    try:
        # Process attachments if provided
        attachments = []
        if args.attachments:
            from src.models.attachments import AttachmentProcessor

            print(f"Processing {len(args.attachments)} attachment(s)...")
            for path in args.attachments:
                try:
                    attachment = AttachmentProcessor.load_from_path(path)
                    attachments.append(attachment)
                    print(f"  {attachment.metadata.filename} ({attachment.metadata.file_type.value})")
                except FileNotFoundError:
                    print(f"  File not found: {path}")
                    print(f"     Tip: Check the file path and try using an absolute path")
                    continue
                except Exception as e:
                    print(f"  Failed to load {path}: {e}")
                    print(f"     Tip: Supported formats are images (JPEG, PNG, WebP) and PDFs")
                    continue

        # Solve the problem
        query_preview = args.problem[:100] + "..." if len(args.problem) > 100 else args.problem
        logger.info(f"Workflow started: mode={args.mode}, experts={args.experts}, query='{query_preview}'")

        start_time = time.time()
        solution = await workflow.solve_problem(args.problem, attachments=attachments)
        elapsed = time.time() - start_time

        logger.info(f"Workflow completed successfully in {elapsed:.1f}s")

        # Record successful query for quota tracking
        quota_status = record_query()

        # Success feedback with timing and quota
        print(f"\nAnalysis complete in {elapsed:.1f}s")
        print(f"Queries remaining: {quota_status.remaining_today} today, {quota_status.remaining_this_hour} this hour")

        # Save memory state if we have a session
        if args.memory_session and memory_persistence:
            memory_persistence.save_state()
            conv_count = len(memory_persistence.memory_manager.conversation_history)
            print(f"\nSession saved ({conv_count} conversation{'s' if conv_count != 1 else ''})")

        # Display final result - adapt based on output destination
        if sys.stdout.isatty():
            # Direct terminal - use Rich rendering for beautiful output
            from src.ui.display import ConsoleDisplay

            display = ConsoleDisplay()
            display._display_smart_content(solution.final_solution)
        else:
            # Piped to TUI/file - output plain markdown for consumer to render
            print("\n" + solution.final_solution + "\n")

        # Helpful hint for copying output
        if not args.markdown:
            print("Tip: Select and copy the text above, or use --markdown to save to file\n")

        # Handle markdown output - pass structured result for elite formatting
        if args.markdown:
            from src.utils.markdown_output import set_workflow_result

            set_workflow_result(solution)

    except KeyboardInterrupt:
        print("\nStopped by user")
        logger.warning("Workflow cancelled by user (KeyboardInterrupt)")
    except MissingAPIKeyError as e:
        print(f"Missing API Key: {e.provider}")
        print(f"Add {e.provider.upper()}_API_KEY to your .env file")
        print("Get your key from: https://console.anthropic.com/ (or respective provider)")
        logger.error(f"Missing API key: {e.provider}")
    except InvalidProviderError as e:
        print(f"{e}")
        if e.available_providers:
            print(f"Available providers: {', '.join(e.available_providers)}")
            print(f"Try: --provider {e.available_providers[0]}")
        logger.error(f"Invalid provider: {e}")
    except (AgentResponseError, AgentTimeoutError) as e:
        print(f"Agent Communication Error: {e}")
        print("The AI service may be experiencing issues. Try again in a moment.")
        import traceback
        tb = traceback.format_exc()
        traceback.print_exc()
        logger.error(f"Agent error: {e}\n{tb}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        tb = traceback.format_exc()
        traceback.print_exc()
        logger.error(f"Workflow failed: {e}\n{tb}")
    finally:
        # Save markdown if capture was enabled
        if args.markdown:
            from src.utils.markdown_output import save_markdown

            md_path = save_markdown(args.markdown_filename)
            if md_path:
                print(f"Output saved to: {md_path}")

        # Clean up
        await workflow.close()

        # Give AutoGen background tasks time to complete
        await asyncio.sleep(0.1)


def main():
    """Synchronous entry point for CLI"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
