"""
Markdown output for Consult
Clean, structured documentation of expert panel consensus

Copyright (c) 2024-2025 Consult. All Rights Reserved.
See LICENSE file for terms. Commercial use requires a separate license.

Outputs are saved to ~/.consult/outputs/ with YAML front matter for traceability.
"""

import os
import re
from datetime import datetime, timezone
from typing import Optional

from src.core.paths import get_outputs_dir
from src.core.identity import slugify, get_iso_timestamp
from src.core.license import get_license_manager, get_current_tier
from src.core.security import redact_secrets


def slugify_query(query: str, max_words: int = 5) -> str:
    """Create a simple slug from query - first N words, alphanumeric only."""
    words = re.findall(r'[a-z0-9]+', query.lower())[:max_words]
    if not words:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    return "-".join(words)


class MarkdownOutputCapture:
    """Generates structured Markdown documentation from workflow results.

    Outputs are saved to ~/.consult/outputs/ with YAML front matter containing
    traceability metadata (user ID, session ID, timestamp, etc.).
    """

    def __init__(self, output_dir: Optional[str] = None, user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Initialize markdown output capture.

        Args:
            output_dir: Output directory. If None, uses ~/.consult/outputs/
            user_id: User ID for traceability. If None, uses license manager.
            session_id: Session ID for traceability.
        """
        self.output_dir = output_dir or str(get_outputs_dir())
        self._user_id = user_id or get_license_manager().get_user_id()
        self._session_id = session_id or "unknown"
        self.workflow_result = None
        os.makedirs(self.output_dir, exist_ok=True)

    def set_workflow_result(self, result):
        """Set the structured workflow result"""
        self.workflow_result = result

    def save(self, filename: Optional[str] = None) -> str:
        """Save structured markdown to file with YAML front matter.

        Output files include traceability metadata and never contain API keys.
        """
        if not self.workflow_result:
            return ""

        if not filename:
            # Generate traceable filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            query_slug = slugify_query(self.workflow_result.problem_statement or "query")
            filename = f"output_{timestamp}_u{self._user_id}_s{self._session_id}_{query_slug}.md"

        filepath = os.path.join(self.output_dir, filename)

        try:
            should_append = filename and os.path.exists(filepath)
            content = self._generate_structured_markdown(self.workflow_result)

            # Redact any secrets before saving
            content = redact_secrets(content)

            mode = 'a' if should_append else 'w'
            with open(filepath, mode, encoding='utf-8') as f:
                if should_append:
                    f.write("\n\n---\n\n# Follow-up Query\n\n")
                else:
                    # Add YAML front matter for new files
                    f.write(self._generate_front_matter())
                f.write(content)

            return filepath
        except Exception as e:
            print(f"Error saving Markdown: {e}")
            return ""

    def _generate_front_matter(self) -> str:
        """Generate YAML front matter with traceability metadata."""
        from src import __version__

        result = self.workflow_result
        experts = list(result.expert_solutions.keys()) if result.expert_solutions else []

        front_matter = f"""---
consult_version: {__version__}
user_id: {self._user_id}
session_id: {self._session_id}
timestamp: {get_iso_timestamp()}
query: "{(result.problem_statement or '').replace('"', "'")[:100]}"
experts: [{', '.join(experts)}]
consensus_score: {result.consensus_score:.2f if result.consensus_score else 0}
tier: {get_current_tier().value}
duration_seconds: {result.total_duration_seconds:.1f if result.total_duration_seconds else 0}
---

"""
        return front_matter

    def _generate_structured_markdown(self, result) -> str:
        """Generate lean, reader-focused Markdown"""

        # Helpers
        duration = result.total_duration_seconds
        duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{duration:.1f}s"
        consensus_pct = f"{result.consensus_score:.0%}" if result.consensus_score else "N/A"
        expert_count = len(result.expert_solutions) if result.expert_solutions else 0

        def clean_name(name):
            return name.replace('_expert', '').replace('_', ' ').title()

        md = []

        # Header - question as the lead
        md.append(f"""# Consult Analysis

> {result.problem_statement}

---

## Recommendation

{self._format_solution(result.final_solution)}
""")

        # Expert perspectives - collapsible
        if result.expert_solutions:
            md.append("""
---

<details>
<summary><strong>Expert Perspectives</strong></summary>
""")
            for name, solution in result.expert_solutions.items():
                md.append(f"""
### {clean_name(name)}

{self._clean_text(solution)}
""")
            md.append("\n</details>")

        # Footer - subtle metadata
        expert_names = ", ".join(clean_name(n) for n in result.expert_solutions.keys()) if result.expert_solutions else ""
        md.append(f"""

---

*{expert_count} experts ({expert_names}) · {consensus_pct} consensus · {result.iterations_completed} iterations · {duration_str}*
""")

        return "\n".join(md)

    def _format_solution(self, solution: str) -> str:
        """Format the main solution text for readability"""
        if not solution:
            return "*No solution provided*"

        # Clean ANSI codes
        clean = self._clean_text(solution)

        # If it's already well-formatted markdown, return as-is
        if any(marker in clean for marker in ['##', '**', '- ', '1. ']):
            return clean

        # Otherwise, ensure proper paragraph breaks
        paragraphs = clean.split('\n\n')
        formatted = []

        for para in paragraphs:
            para = para.strip()
            if para:
                formatted.append(para)

        return '\n\n'.join(formatted)

    def _clean_text(self, text: str) -> str:
        """Clean text of ANSI codes and normalize whitespace"""
        if not text:
            return ""

        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean = ansi_escape.sub('', text)

        # Remove excessive whitespace while preserving structure
        lines = clean.split('\n')
        cleaned_lines = []
        prev_empty = False

        for line in lines:
            line = line.rstrip()
            is_empty = not line.strip()

            # Skip multiple consecutive empty lines
            if is_empty and prev_empty:
                continue

            cleaned_lines.append(line)
            prev_empty = is_empty

        return '\n'.join(cleaned_lines).strip()


# Global instance for CLI usage
_markdown_capture = MarkdownOutputCapture()


def set_workflow_result(result):
    """Set the workflow result for structured markdown generation"""
    _markdown_capture.set_workflow_result(result)


def save_markdown(filename: Optional[str] = None) -> str:
    """Save markdown from workflow result"""
    return _markdown_capture.save(filename)


def generate_document(result, output_path: Optional[str] = None, append: bool = False) -> str:
    """Generate a markdown document from workflow result.

    Args:
        result: Workflow result object
        output_path: Path to save the file
        append: If True, append to existing file with separator
    """
    capture = MarkdownOutputCapture()
    content = capture._generate_structured_markdown(result)

    # SECURITY: Redact any secrets before writing to file
    content = redact_secrets(content)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        if append and os.path.exists(output_path):
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write("\n\n---\n\n# Follow-up\n\n")
                f.write(content)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return output_path

    return content
