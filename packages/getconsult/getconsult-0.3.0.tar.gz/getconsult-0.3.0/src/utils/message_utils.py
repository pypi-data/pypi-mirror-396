"""Message utilities for handling multi-modal messages across providers"""

from typing import List, Dict, Any, Union, Optional
from ..models.attachments import Attachment, AttachmentType


class MessageUtils:
    """Utilities for creating provider-compatible multi-modal messages"""
    
    @staticmethod
    def create_multimodal_message(text: str, attachments: List[Attachment], provider: str) -> List[Dict[str, Any]]:
        """Create a multi-modal message compatible with the specified provider.

        NOTE: Expects attachments to be pre-prepared by AttachmentManager.prepare_for_provider().
        PDFs should already be converted to images for OpenAI, and kept native for Anthropic/Google.

        Args:
            text: Text content
            attachments: Pre-prepared attachments from AttachmentManager
            provider: Target provider (anthropic, openai, google)
        """
        if not attachments:
            return [{"role": "user", "content": text}]

        # Create content based on provider format
        # Attachments are already provider-ready from AttachmentManager
        if provider == "anthropic":
            return MessageUtils._create_anthropic_message(text, attachments)
        elif provider == "openai":
            return MessageUtils._create_openai_message(text, attachments)
        elif provider == "google":
            return MessageUtils._create_google_message(text, attachments)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _create_anthropic_message(text: str, attachments: List[Attachment]) -> List[Dict[str, Any]]:
        """Create Anthropic-compatible multi-modal message"""
        content = []
        
        # Add text content
        if text.strip():
            content.append({
                "type": "text",
                "text": text
            })
        
        # Add attachments
        for attachment in attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": attachment.mime_type,
                        "data": attachment.to_base64()
                    }
                })
            elif attachment.metadata.file_type == AttachmentType.PDF:
                # Anthropic supports PDF directly
                content.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": attachment.mime_type,
                        "data": attachment.to_base64()
                    }
                })
        
        return [{"role": "user", "content": content}]
    
    @staticmethod
    def _create_openai_message(text: str, attachments: List[Attachment]) -> List[Dict[str, Any]]:
        """Create OpenAI-compatible multi-modal message"""
        content = []
        
        # Add text content
        if text.strip():
            content.append({
                "type": "text",
                "text": text
            })
        
        # Add images (PDFs already converted to images)
        for attachment in attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": attachment.get_data_url(),
                        "detail": "high"
                    }
                })
        
        return [{"role": "user", "content": content}]
    
    @staticmethod
    def _create_google_message(text: str, attachments: List[Attachment]) -> List[Dict[str, Any]]:
        """Create Google Gemini-compatible multi-modal message"""
        parts = []
        
        # Add text content
        if text.strip():
            parts.append({"text": text})
        
        # Add attachments
        for attachment in attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                parts.append({
                    "inline_data": {
                        "mime_type": attachment.mime_type,
                        "data": attachment.to_base64()
                    }
                })
            elif attachment.metadata.file_type == AttachmentType.PDF:
                # Google supports PDF directly
                parts.append({
                    "inline_data": {
                        "mime_type": attachment.mime_type,
                        "data": attachment.to_base64()
                    }
                })
        
        return [{"role": "user", "parts": parts}]
    
    @staticmethod
    def format_attachment_summary(attachments: List[Attachment]) -> str:
        """Create a human-readable summary of attachments for context"""
        if not attachments:
            return ""
        
        summary_parts = []
        for attachment in attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                summary_parts.append(f"📷 Image: {attachment.metadata.filename} ({attachment.metadata.width}x{attachment.metadata.height})")
            elif attachment.metadata.file_type == AttachmentType.PDF:
                summary_parts.append(f"📄 PDF: {attachment.metadata.filename} ({attachment.metadata.pages} pages)")
        
        return "\n" + "\n".join(summary_parts) + "\n"
    
    @staticmethod
    def append_attachment_context(text: str, attachments: List[Attachment]) -> str:
        """Append attachment context to text prompt for better AI understanding"""
        if not attachments:
            return text
        
        attachment_summary = MessageUtils.format_attachment_summary(attachments)
        context_text = f"\n\nI've attached the following files for your analysis:{attachment_summary}"
        context_text += "Please analyze these attachments along with the text query above and provide comprehensive insights that consider both the textual question and the visual/document content."
        
        return text + context_text


class MultiModalAgentWrapper:
    """Wrapper to make existing agents multi-modal capable"""
    
    def __init__(self, base_agent, provider: str):
        self.base_agent = base_agent
        self.provider = provider
    
    async def agenerate_reply(self, messages, **kwargs):
        """Enhanced reply generation that handles multi-modal messages"""
        # Extract last message to check for attachments
        if not messages:
            return await self.base_agent.agenerate_reply(messages, **kwargs)
        
        last_message = messages[-1]
        
        # Check if we have multimodal content
        if isinstance(last_message.get("content"), list):
            # Already multimodal - pass through
            return await self.base_agent.agenerate_reply(messages, **kwargs)
        
        # Standard text-only message - pass through
        return await self.base_agent.agenerate_reply(messages, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all other attributes to base agent"""
        return getattr(self.base_agent, name)