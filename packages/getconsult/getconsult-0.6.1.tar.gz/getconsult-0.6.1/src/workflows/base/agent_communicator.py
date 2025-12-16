"""Clean agent communication logic"""
import asyncio
import time
import uuid
from typing import List, Optional
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from ...utils.message_utils import MessageUtils
from ...core.exceptions import AgentResponseError, AgentTimeoutError, MultimodalProcessingError
from ...core.paths import get_logs_dir
from ...core.security import get_contextual_logger

# Module logger - initialized lazily
_logger = None


def _get_logger():
    """Get or create the agent communicator logger."""
    global _logger
    if _logger is None:
        log_file = get_logs_dir() / "consult.log"
        _logger = get_contextual_logger("consult.agent_comm", log_file=str(log_file))
    return _logger


class AgentCommunicator:
    """Handle agent communication with clean error handling"""

    def __init__(self):
        self.logger = _get_logger()
    
    async def get_response(self, agent, prompt: str, max_messages: int = 2, attachments: Optional[List] = None) -> str:
        """Get response from agent with clean error handling - moved from workflow"""
        response = ""
        chat = None
        start_time = time.time()

        # Extract agent info for logging
        agent_name = getattr(agent, 'name', 'unknown')
        model_name = 'unknown'
        provider = 'unknown'
        if hasattr(agent, '_model_client'):
            model_name = getattr(agent._model_client, 'model', model_name)
            # Infer provider from model name
            if 'claude' in model_name.lower():
                provider = 'anthropic'
            elif 'gpt' in model_name.lower() or 'o1' in model_name.lower():
                provider = 'openai'
            elif 'gemini' in model_name.lower():
                provider = 'google'

        # Generate request ID for correlation (local tracking - provider IDs not exposed by AutoGen)
        request_id = uuid.uuid4().hex[:8]

        prompt_preview = prompt[:80] + '...' if len(prompt) > 80 else prompt
        self.logger.info(f"[{provider}] {agent_name} starting | req={request_id} | model={model_name} | prompt='{prompt_preview}'")

        try:
            # Build chat parameters
            chat_params = {
                "participants": [agent],
                "termination_condition": MaxMessageTermination(max_messages)
            }

            # Register custom message types if agent uses structured output
            # Required for AutoGen 0.6.2+ (see: github.com/microsoft/autogen/issues/6795)
            if hasattr(agent, '_output_content_type') and agent._output_content_type is not None:
                from autogen_agentchat.messages import StructuredMessage
                chat_params["custom_message_types"] = [StructuredMessage[agent._output_content_type]]

            # Create chat
            chat = RoundRobinGroupChat(**chat_params)

            # Prepare task with multimodal content if attachments are provided
            if attachments:
                # Check if model supports vision for multimodal content
                supports_vision = agent._model_client.model_info.get('vision', False)

                if supports_vision:
                    # Use multimodal message for vision-capable models
                    task_content = self._create_multimodal_message(prompt, attachments)
                    self.logger.debug(f"[{provider}] {agent_name} using multimodal message with {len(attachments)} attachment(s)")
                else:
                    # Fallback to text descriptions for non-vision models
                    task_content = MessageUtils.append_attachment_context(prompt, attachments)
                    self.logger.debug(f"[{provider}] {agent_name} using text fallback for {len(attachments)} attachment(s)")
            else:
                task_content = prompt

            # Use run() instead of run_stream() to get complete response
            # run_stream() can yield partial chunks that overwrite each other
            # run() returns the final TaskResult with complete messages
            result = await chat.run(task=task_content)

            # Extract complete response from TaskResult
            # LLM may split response across multiple messages - concatenate all from this agent
            if hasattr(result, 'messages') and result.messages:
                agent_parts = []
                for msg in result.messages:
                    if hasattr(msg, 'source') and msg.source == agent.name:
                        if hasattr(msg, 'content') and msg.content:
                            agent_parts.append(self._normalize_response_content(msg.content))
                response = ''.join(agent_parts)

            elapsed = time.time() - start_time
            response_len = len(response)
            self.logger.info(f"[{provider}] {agent_name} completed | req={request_id} | {elapsed:.2f}s | {response_len} chars")

        except asyncio.CancelledError:
            elapsed = time.time() - start_time
            self.logger.error(f"[{provider}] {agent_name} TIMEOUT | req={request_id} | after {elapsed:.2f}s")
            raise AgentTimeoutError(agent.name, max_messages * 30.0)  # Estimate timeout
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"[{provider}] {agent_name} FAILED | req={request_id} | after {elapsed:.2f}s | error={type(e).__name__}: {e}")
            raise AgentResponseError(agent.name, prompt, e)
        finally:
            # Clean cleanup
            chat = None

        return response
    
    async def get_parallel_responses(self, agents, prompts) -> list:
        """Get responses from multiple agents in parallel"""
        if len(agents) != len(prompts):
            raise ValueError("Agents and prompts lists must have same length")

        agent_names = [getattr(a, 'name', 'unknown') for a in agents]
        self.logger.info(f"Parallel request starting | {len(agents)} agents: {', '.join(agent_names)}")
        start_time = time.time()

        tasks = []
        for agent, prompt in zip(agents, prompts):
            task = self.get_response(agent, prompt)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        fail_count = len(results) - success_count
        self.logger.info(f"Parallel request completed | {elapsed:.2f}s | {success_count} succeeded, {fail_count} failed")

        return results
    
    def _create_multimodal_message(self, prompt: str, attachments: List):
        """Create multimodal message for AutoGen 0.4+ format.

        Expects attachments to be pre-prepared by AttachmentManager.prepare_for_provider()
        which converts all PDFs to images. AutoGen only supports strings and Image objects.

        Args:
            prompt: Text prompt
            attachments: List of Attachment objects (all images after preparation)
        """
        from autogen_core import Image
        from autogen_agentchat.messages import MultiModalMessage
        from PIL import Image as PILImage
        import io

        content_parts = []

        # Add text content
        if prompt.strip():
            content_parts.append(prompt)

        # Add images (PDFs already converted by AttachmentManager)
        for attachment in attachments:
            if attachment.metadata.file_type.value == "image":
                pil_image = PILImage.open(io.BytesIO(attachment.data))
                autogen_image = Image(pil_image)
                content_parts.append(autogen_image)

        # Create MultiModalMessage with content
        return MultiModalMessage(content=content_parts, source="user")
    
    def _normalize_response_content(self, content) -> str:
        """Normalize response content to string format for consistent handling

        Different AI providers may return content in different formats:
        - Anthropic/OpenAI: string
        - Google Gemini: sometimes list of strings or mixed content
        - Structured output: Pydantic model instance (serialize to JSON)
        """
        if isinstance(content, str):
            return content
        elif hasattr(content, 'model_dump_json'):
            # Pydantic model - serialize to JSON for structured output
            return content.model_dump_json()
        elif hasattr(content, 'json'):
            # Older Pydantic v1 style
            return content.json()
        elif isinstance(content, list):
            # Handle list responses from providers like Google Gemini
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif hasattr(item, 'text') and isinstance(item.text, str):
                    # Handle structured content objects with text property
                    text_parts.append(item.text)
                elif hasattr(item, 'content') and isinstance(item.content, str):
                    # Handle structured content objects with content property
                    text_parts.append(item.content)
                else:
                    # Convert other types to string representation
                    text_parts.append(str(item))
            return ''.join(text_parts)
        else:
            # Handle any other content types
            return str(content)