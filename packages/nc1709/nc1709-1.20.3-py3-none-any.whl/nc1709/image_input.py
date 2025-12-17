"""
Image Input Support for NC1709

Provides multi-modal capabilities for image/screenshot input:
- Read and encode images for LLM API calls
- Support for PNG, JPG, GIF, WebP formats
- Screenshot capture (macOS support)
- Clipboard image paste support
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import subprocess
import tempfile


# Supported image formats
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
SUPPORTED_MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
}


@dataclass
class ImageData:
    """Represents an image for multi-modal input"""
    path: str
    base64_data: str
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: int = 0


def is_image_file(file_path: str) -> bool:
    """Check if a file is a supported image format"""
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def get_image_mime_type(file_path: str) -> str:
    """Get MIME type for an image file"""
    path = Path(file_path)
    ext = path.suffix.lower()
    return SUPPORTED_MIME_TYPES.get(ext, 'image/png')


def encode_image_to_base64(file_path: str) -> Optional[str]:
    """
    Read an image file and encode it to base64.

    Args:
        file_path: Path to the image file

    Returns:
        Base64 encoded string, or None if failed
    """
    path = Path(file_path).expanduser()

    if not path.exists():
        return None

    if not is_image_file(str(path)):
        return None

    try:
        with open(path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception:
        return None


def load_image(file_path: str) -> Optional[ImageData]:
    """
    Load an image file and prepare it for multi-modal input.

    Args:
        file_path: Path to the image file

    Returns:
        ImageData object, or None if failed
    """
    path = Path(file_path).expanduser()

    if not path.exists():
        return None

    if not is_image_file(str(path)):
        return None

    base64_data = encode_image_to_base64(str(path))
    if not base64_data:
        return None

    # Get file size
    size_bytes = path.stat().st_size

    # Try to get image dimensions (optional, requires PIL)
    width, height = None, None
    try:
        from PIL import Image
        with Image.open(path) as img:
            width, height = img.size
    except ImportError:
        pass
    except Exception:
        pass

    return ImageData(
        path=str(path.absolute()),
        base64_data=base64_data,
        mime_type=get_image_mime_type(str(path)),
        width=width,
        height=height,
        size_bytes=size_bytes
    )


def capture_screenshot(output_path: Optional[str] = None) -> Optional[str]:
    """
    Capture a screenshot (macOS only for now).

    Args:
        output_path: Optional path to save screenshot (uses temp file if not provided)

    Returns:
        Path to the saved screenshot, or None if failed
    """
    import platform

    if platform.system() != 'Darwin':
        return None

    if output_path is None:
        # Create a temporary file
        fd, output_path = tempfile.mkstemp(suffix='.png', prefix='nc1709_screenshot_')
        os.close(fd)

    try:
        # Use macOS screencapture command
        # -i for interactive selection, -x for no sound
        result = subprocess.run(
            ['screencapture', '-i', '-x', output_path],
            capture_output=True,
            timeout=60
        )

        if result.returncode == 0 and Path(output_path).exists():
            return output_path
        else:
            # User cancelled or error
            if Path(output_path).exists():
                os.remove(output_path)
            return None

    except subprocess.TimeoutExpired:
        if Path(output_path).exists():
            os.remove(output_path)
        return None
    except Exception:
        return None


def get_clipboard_image() -> Optional[str]:
    """
    Get image from clipboard (macOS only for now).

    Returns:
        Path to temporary file containing the image, or None if no image in clipboard
    """
    import platform

    if platform.system() != 'Darwin':
        return None

    try:
        # Create temp file for clipboard image
        fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='nc1709_clipboard_')
        os.close(fd)

        # Use pngpaste or osascript to get clipboard image
        # First try pngpaste if available
        result = subprocess.run(
            ['which', 'pngpaste'],
            capture_output=True
        )

        if result.returncode == 0:
            # pngpaste is available
            result = subprocess.run(
                ['pngpaste', temp_path],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and Path(temp_path).exists():
                return temp_path
        else:
            # Fallback to osascript
            script = '''
            tell application "System Events"
                set clipboardData to the clipboard as «class PNGf»
            end tell
            '''
            # This is more complex, skip for now
            pass

        # Cleanup if failed
        if Path(temp_path).exists():
            os.remove(temp_path)
        return None

    except Exception:
        return None


def format_image_for_api(image: ImageData, api_type: str = "anthropic") -> Dict[str, Any]:
    """
    Format image data for API request.

    Args:
        image: ImageData object
        api_type: API type ("anthropic", "openai")

    Returns:
        Dict formatted for the API
    """
    if api_type == "anthropic":
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image.mime_type,
                "data": image.base64_data
            }
        }
    elif api_type == "openai":
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{image.mime_type};base64,{image.base64_data}"
            }
        }
    else:
        raise ValueError(f"Unknown API type: {api_type}")


def extract_image_references(text: str) -> List[str]:
    """
    Extract image file references from text.

    Supports formats like:
    - @image:path/to/image.png
    - [image: path/to/image.jpg]
    - {{image: /absolute/path.png}}

    Args:
        text: Input text

    Returns:
        List of image paths found
    """
    import re

    patterns = [
        r'@image:([^\s]+)',
        r'\[image:\s*([^\]]+)\]',
        r'\{\{image:\s*([^}]+)\}\}',
    ]

    image_paths = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        image_paths.extend([m.strip() for m in matches])

    return image_paths


def process_prompt_with_images(
    prompt: str,
    additional_images: Optional[List[str]] = None
) -> Tuple[str, List[ImageData]]:
    """
    Process a prompt and extract/load any referenced images.

    Args:
        prompt: User prompt text
        additional_images: Optional list of additional image paths

    Returns:
        Tuple of (cleaned prompt, list of ImageData)
    """
    import re

    images = []
    cleaned_prompt = prompt

    # Extract image references from prompt
    image_paths = extract_image_references(prompt)

    # Add additional images
    if additional_images:
        image_paths.extend(additional_images)

    # Load each image
    for path in image_paths:
        image = load_image(path)
        if image:
            images.append(image)
        else:
            # Keep the reference but note it failed
            print(f"Warning: Could not load image: {path}")

    # Clean the prompt by removing image references
    patterns = [
        r'@image:[^\s]+',
        r'\[image:\s*[^\]]+\]',
        r'\{\{image:\s*[^}]+\}\}',
    ]
    for pattern in patterns:
        cleaned_prompt = re.sub(pattern, '', cleaned_prompt, flags=re.IGNORECASE)

    # Clean up extra whitespace
    cleaned_prompt = ' '.join(cleaned_prompt.split())

    return cleaned_prompt, images


def get_image_info(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Get information about an image file.

    Args:
        file_path: Path to the image

    Returns:
        Dict with image info, or None if failed
    """
    path = Path(file_path).expanduser()

    if not path.exists() or not is_image_file(str(path)):
        return None

    info = {
        "path": str(path.absolute()),
        "name": path.name,
        "format": path.suffix.lower()[1:],
        "size_bytes": path.stat().st_size,
        "size_human": format_file_size(path.stat().st_size),
    }

    # Try to get dimensions
    try:
        from PIL import Image
        with Image.open(path) as img:
            info["width"] = img.width
            info["height"] = img.height
            info["mode"] = img.mode
    except ImportError:
        pass
    except Exception:
        pass

    return info


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class ImageInputHandler:
    """
    Handler for image input in the CLI.

    Provides methods for:
    - Loading images from paths
    - Capturing screenshots
    - Managing image context for prompts
    """

    def __init__(self):
        self._pending_images: List[ImageData] = []

    def add_image(self, path: str) -> bool:
        """Add an image to the pending list"""
        image = load_image(path)
        if image:
            self._pending_images.append(image)
            return True
        return False

    def add_screenshot(self) -> bool:
        """Capture and add a screenshot"""
        path = capture_screenshot()
        if path:
            return self.add_image(path)
        return False

    def add_clipboard(self) -> bool:
        """Add image from clipboard"""
        path = get_clipboard_image()
        if path:
            return self.add_image(path)
        return False

    def get_pending_images(self) -> List[ImageData]:
        """Get all pending images"""
        return self._pending_images.copy()

    def clear_pending(self) -> None:
        """Clear pending images"""
        self._pending_images = []

    def has_pending_images(self) -> bool:
        """Check if there are pending images"""
        return len(self._pending_images) > 0

    def format_for_api(self, api_type: str = "anthropic") -> List[Dict[str, Any]]:
        """Format pending images for API request"""
        return [format_image_for_api(img, api_type) for img in self._pending_images]


# Global image handler
_image_handler: Optional[ImageInputHandler] = None


def get_image_handler() -> ImageInputHandler:
    """Get or create the global image handler"""
    global _image_handler
    if _image_handler is None:
        _image_handler = ImageInputHandler()
    return _image_handler
