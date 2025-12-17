"""Attachment models and utilities for multi-modal support"""

from typing import Dict, List, Literal, Optional, Union, Any
from enum import Enum
from pathlib import Path
import base64
import mimetypes
import io
from PIL import Image
import fitz  # PyMuPDF for PDF handling


class AttachmentType(str, Enum):
    """Supported attachment types"""
    IMAGE = "image"
    PDF = "pdf"


class ImageFormat(str, Enum):
    """Supported image formats across all providers"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    # Additional formats supported by some providers
    GIF = "gif"  # OpenAI only (non-animated)
    HEIC = "heic"  # Google only
    HEIF = "heif"  # Google only


class AttachmentMetadata:
    """Metadata for an attachment"""
    
    def __init__(
        self,
        filename: str,
        file_type: AttachmentType,
        format: Optional[str] = None,
        size_bytes: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        pages: Optional[int] = None
    ):
        self.filename = filename
        self.file_type = file_type
        self.format = format
        self.size_bytes = size_bytes
        self.width = width
        self.height = height
        self.pages = pages


class Attachment:
    """Universal attachment representation"""
    
    def __init__(
        self,
        data: bytes,
        metadata: AttachmentMetadata,
        mime_type: str
    ):
        self.data = data
        self.metadata = metadata
        self.mime_type = mime_type
    
    def to_base64(self) -> str:
        """Convert attachment data to base64 string"""
        return base64.b64encode(self.data).decode('utf-8')
    
    def get_data_url(self) -> str:
        """Get data URL for the attachment"""
        return f"data:{self.mime_type};base64,{self.to_base64()}"
    
    def is_supported_by_provider(self, provider: str) -> bool:
        """Check if attachment is supported by a specific provider"""
        return AttachmentValidator.is_supported(self, provider)


class AttachmentValidator:
    """Validates attachments against provider capabilities"""
    
    # Provider capability matrix
    # pdf: "native" = provider handles PDF directly, "convert" = must convert to images
    PROVIDER_FORMATS = {
        "openai": {
            "image": ["jpeg", "png", "webp", "gif"],
            "pdf": "convert"  # OpenAI requires conversion to images
        },
        "anthropic": {
            "image": ["jpeg", "png", "webp", "gif"],
            "pdf": "native"  # Anthropic supports native PDF
        },
        "google": {
            "image": ["jpeg", "png", "webp", "heic", "heif"],
            "pdf": "native"  # Google supports native PDF
        }
    }
    
    # Size limits per provider (in MB)
    PROVIDER_LIMITS = {
        "openai": {"max_file_size": 20, "max_images_per_request": 10},
        "anthropic": {"max_file_size": 20, "max_images_per_request": 20, "max_pdf_pages": 100},
        "google": {"max_file_size": 20, "max_images_per_request": 3600, "max_pdf_pages": 1000}
    }
    
    @classmethod
    def is_supported(cls, attachment: Attachment, provider: str) -> bool:
        """Check if attachment is supported by provider"""
        if provider not in cls.PROVIDER_FORMATS:
            return False
        
        provider_caps = cls.PROVIDER_FORMATS[provider]
        
        if attachment.metadata.file_type == AttachmentType.IMAGE:
            return attachment.metadata.format in provider_caps.get("image", [])
        elif attachment.metadata.file_type == AttachmentType.PDF:
            return provider_caps.get("pdf", False)
        
        return False
    
    @classmethod
    def validate_size(cls, attachment: Attachment, provider: str) -> bool:
        """Validate attachment size against provider limits"""
        if provider not in cls.PROVIDER_LIMITS:
            return False
        
        limits = cls.PROVIDER_LIMITS[provider]
        size_mb = attachment.metadata.size_bytes / (1024 * 1024)
        
        if size_mb > limits["max_file_size"]:
            return False
        
        if attachment.metadata.file_type == AttachmentType.PDF and attachment.metadata.pages:
            max_pages = limits.get("max_pdf_pages")
            if max_pages and attachment.metadata.pages > max_pages:
                return False
        
        return True
    
    @classmethod
    def get_common_formats(cls) -> Dict[str, List[str]]:
        """Get formats supported by all providers"""
        all_providers = list(cls.PROVIDER_FORMATS.keys())
        common_image_formats = set(cls.PROVIDER_FORMATS[all_providers[0]]["image"])
        
        for provider in all_providers[1:]:
            common_image_formats &= set(cls.PROVIDER_FORMATS[provider]["image"])
        
        return {
            "image": list(common_image_formats),
            "pdf": ["pdf"] if all(cls.PROVIDER_FORMATS[p]["pdf"] for p in all_providers) else []
        }


class AttachmentProcessor:
    """Processes attachments for different providers"""
    
    @staticmethod
    def load_from_path(file_path: Union[str, Path]) -> Attachment:
        """Load attachment from file path"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file data
        data = path.read_bytes()
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            raise ValueError(f"Cannot determine MIME type for: {path.name}")
        
        # Create metadata
        metadata = AttachmentProcessor._extract_metadata(data, path.name, mime_type)
        
        return Attachment(data, metadata, mime_type)
    
    @staticmethod
    def _extract_metadata(data: bytes, filename: str, mime_type: str) -> AttachmentMetadata:
        """Extract metadata from file data"""
        size_bytes = len(data)
        
        if mime_type.startswith("image/"):
            return AttachmentProcessor._extract_image_metadata(data, filename, size_bytes)
        elif mime_type == "application/pdf":
            return AttachmentProcessor._extract_pdf_metadata(data, filename, size_bytes)
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")
    
    @staticmethod
    def _extract_image_metadata(data: bytes, filename: str, size_bytes: int) -> AttachmentMetadata:
        """Extract image metadata"""
        try:
            with Image.open(io.BytesIO(data)) as img:
                format_lower = img.format.lower() if img.format else "unknown"
                width, height = img.size
                
                return AttachmentMetadata(
                    filename=filename,
                    file_type=AttachmentType.IMAGE,
                    format=format_lower,
                    size_bytes=size_bytes,
                    width=width,
                    height=height
                )
        except Exception as e:
            raise ValueError(f"Cannot process image {filename}: {e}")
    
    @staticmethod
    def _extract_pdf_metadata(data: bytes, filename: str, size_bytes: int) -> AttachmentMetadata:
        """Extract PDF metadata"""
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            pages = len(doc)
            doc.close()
            
            return AttachmentMetadata(
                filename=filename,
                file_type=AttachmentType.PDF,
                format="pdf",
                size_bytes=size_bytes,
                pages=pages
            )
        except Exception as e:
            raise ValueError(f"Cannot process PDF {filename}: {e}")
    
    @staticmethod
    def convert_pdf_to_images(attachment: Attachment, dpi: int = 200) -> List[Attachment]:
        """Convert PDF to images for providers that don't support native PDF"""
        if attachment.metadata.file_type != AttachmentType.PDF:
            raise ValueError("Attachment is not a PDF")
        
        try:
            doc = fitz.open(stream=attachment.data, filetype="pdf")
            images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Convert to image
                mat = fitz.Matrix(dpi/72, dpi/72)  # Scale to desired DPI
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Create image metadata
                metadata = AttachmentMetadata(
                    filename=f"{attachment.metadata.filename}_page_{page_num + 1}.png",
                    file_type=AttachmentType.IMAGE,
                    format="png",
                    size_bytes=len(img_data),
                    width=pix.width,
                    height=pix.height
                )
                
                images.append(Attachment(img_data, metadata, "image/png"))
            
            doc.close()
            return images
        except Exception as e:
            raise ValueError(f"Cannot convert PDF to images: {e}")


class AttachmentManager:
    """Manages attachments for multi-provider compatibility"""

    # Standardized DPI for PDF to image conversion
    CONVERSION_DPI = 150

    def __init__(self, provider: str):
        self.provider = provider
        self.attachments: List[Attachment] = []
        # Cache for PDF to image conversions (keyed by filename)
        self._conversion_cache: Dict[str, List[Attachment]] = {}

    def add_attachment(self, attachment: Union[str, Path, Attachment]) -> bool:
        """Add an attachment from file path or existing Attachment object"""
        try:
            # Handle both paths and Attachment objects
            if isinstance(attachment, Attachment):
                att = attachment
            else:
                att = AttachmentProcessor.load_from_path(attachment)

            # Validate against provider
            if not AttachmentValidator.is_supported(att, self.provider):
                raise ValueError(f"Attachment format not supported by {self.provider}")

            if not AttachmentValidator.validate_size(att, self.provider):
                raise ValueError(f"Attachment exceeds size limits for {self.provider}")

            self.attachments.append(att)
            return True
        except Exception as e:
            raise ValueError(f"Cannot add attachment: {e}")
    
    def prepare_for_provider(self) -> List[Attachment]:
        """Prepare attachments for the current provider.

        This is the main method to use before sending attachments to agents.
        Converts PDFs to images for all providers since AutoGen's MultiModalMessage
        only supports strings and Image objects (no native PDF support yet).

        - PDFs: Converted to images (cached to avoid redundant processing)
        - Images: Returned as-is for all providers

        Returns:
            Flat list of Attachment objects ready for the provider (all images)
        """
        # Validate limits before preparing
        if not self.validate_request_limits():
            raise ValueError(f"Attachments exceed request limits for {self.provider}")

        prepared: List[Attachment] = []

        for attachment in self.attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                # Images pass through as-is
                prepared.append(attachment)

            elif attachment.metadata.file_type == AttachmentType.PDF:
                # Always convert PDFs to images (AutoGen doesn't support native PDF)
                # Use cache to avoid redundant conversion across workflow phases
                cache_key = attachment.metadata.filename
                if cache_key in self._conversion_cache:
                    # Use cached conversion
                    prepared.extend(self._conversion_cache[cache_key])
                else:
                    # Convert and cache
                    images = AttachmentProcessor.convert_pdf_to_images(
                        attachment, dpi=self.CONVERSION_DPI
                    )
                    self._conversion_cache[cache_key] = images
                    prepared.extend(images)

        return prepared

    def get_provider_compatible_attachments(self) -> List[Union[Attachment, List[Attachment]]]:
        """Get attachments formatted for the current provider.

        DEPRECATED: Use prepare_for_provider() instead which returns a flat list.
        This method is kept for backward compatibility.
        """
        compatible_attachments = []

        for attachment in self.attachments:
            if attachment.metadata.file_type == AttachmentType.PDF and self.provider == "openai":
                # OpenAI requires PDF to be converted to images
                image_attachments = AttachmentProcessor.convert_pdf_to_images(attachment)
                compatible_attachments.append(image_attachments)
            else:
                compatible_attachments.append(attachment)

        return compatible_attachments
    
    def clear(self):
        """Clear all attachments and conversion cache"""
        self.attachments.clear()
        self._conversion_cache.clear()
    
    def get_attachment_count(self) -> int:
        """Get total number of attachments"""
        return len(self.attachments)
    
    def validate_request_limits(self) -> bool:
        """Validate that attachments don't exceed provider request limits"""
        limits = AttachmentValidator.PROVIDER_LIMITS.get(self.provider, {})
        max_images = limits.get("max_images_per_request", float('inf'))
        
        # Count total images (including PDF pages converted to images)
        image_count = 0
        for attachment in self.attachments:
            if attachment.metadata.file_type == AttachmentType.IMAGE:
                image_count += 1
            elif attachment.metadata.file_type == AttachmentType.PDF and self.provider == "openai":
                image_count += attachment.metadata.pages or 1
        
        return image_count <= max_images