from ._internal import _zelesis_utils
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import io
import os
from PIL import Image



def get_zelesis_path() -> str:
    """
    Returns the path for the zelesis neo installation.
    """
    return _zelesis_utils._find_zelesis_installation()


def get_zelesis_version() -> str:
    """
    Returns the current version of zelesis neo.
    """
    return _zelesis_utils._get_zelesis_version()


class CompressionInfo:
    """
    Information about image compression results.
    """
    
    def __init__(
        self,
        success: bool,
        final_size_kb: float,
        target_size_kb: float,
        original_size_kb: float,
        quality: int,
        dimensions: Tuple[int, int],
        original_dimensions: Tuple[int, int],
        iterations: int,
        note: Optional[str] = None,
    ):
        self.success = success
        self.final_size_kb = final_size_kb
        self.target_size_kb = target_size_kb
        self.original_size_kb = original_size_kb
        self.compression_ratio = (
            original_size_kb / final_size_kb if final_size_kb > 0 else 0.0
        )
        self.quality = quality
        self.dimensions = dimensions
        self.original_dimensions = original_dimensions
        self.iterations = iterations
        self.note = note
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.
        """
        return {
            'success': self.success,
            'final_size_kb': self.final_size_kb,
            'target_size_kb': self.target_size_kb,
            'original_size_kb': self.original_size_kb,
            'compression_ratio': self.compression_ratio,
            'quality': self.quality,
            'dimensions': self.dimensions,
            'original_dimensions': self.original_dimensions,
            'iterations': self.iterations,
            'note': self.note,
        }


def compress_image_to_target_size(
    image_path: str,
    target_kb: int = 100,
    min_quality: int = 10,
    max_quality: int = 95,
    min_dimension: int = 64,
    step_factor: float = 0.8,
    max_iterations: int = 20,
) -> Tuple[bytes, CompressionInfo]:
    """
    Compress an image to fit within a target file size.
    
    Uses iterative compression with quality and dimension adjustments to achieve
    the target file size while maintaining reasonable image quality.
    
    Args:
        image_path: Path to the input image file
        target_kb: Target file size in kilobytes (default: 100KB)
        min_quality: Minimum JPEG quality to try (default: 10)
        max_quality: Maximum JPEG quality to try (default: 95)
        min_dimension: Minimum width/height in pixels (default: 64)
        step_factor: Factor to reduce dimensions each iteration (default: 0.8 = 80%)
        max_iterations: Maximum number of compression attempts (default: 20)
    
    Returns:
        Tuple of (compressed_image_bytes, CompressionInfo)
    
    Raises:
        ImportError: If PIL/Pillow is not installed
        FileNotFoundError: If image file doesn't exist
        ValueError: If image can't be opened or compressed
    
    Example:
        >>> compressed_bytes, info = compress_image_to_target_size("image.png", target_kb=50)
        >>> print(f"Compressed from {info.original_size_kb:.1f}KB to {info.final_size_kb:.1f}KB")
    """
    
    image_path_obj = Path(image_path)
    if not image_path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    target_bytes = target_kb * 1024
    
    # Open the original image
    try:
        img = Image.open(image_path_obj)
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")
    
    # Convert to RGB if necessary (JPEG doesn't support transparency)
    img = _convert_to_rgb(img)
    
    original_size = os.path.getsize(image_path_obj)
    original_dims = img.size
    
    current_width, current_height = img.size
    current_quality = max_quality
    
    best_result: Optional[Tuple[bytes, int, Tuple[int, int]]] = None
    best_size = float('inf')
    
    # Iterative compression loop
    for iteration in range(max_iterations):
        # Resize the image if needed
        resized_img = img.copy()
        if (current_width, current_height) != original_dims:
            resized_img = resized_img.resize(
                (current_width, current_height),
                Image.Resampling.LANCZOS
            )
        
        # Try different quality levels
        quality_levels = [current_quality, max(current_quality - 20, min_quality)]
        for quality in quality_levels:
            buffer = io.BytesIO()
            
            resized_img.save(
                buffer,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )
            
            current_size = buffer.tell()
            
            # Success! We're under the target size
            if current_size <= target_bytes:
                info = CompressionInfo(
                    success=True,
                    final_size_kb=current_size / 1024,
                    target_size_kb=target_kb,
                    original_size_kb=original_size / 1024,
                    quality=quality,
                    dimensions=(current_width, current_height),
                    original_dimensions=original_dims,
                    iterations=iteration + 1,
                )
                return buffer.getvalue(), info
            
            # Track the best result (closest to target but still over)
            if current_size < best_size:
                best_size = current_size
                best_result = (buffer.getvalue(), quality, (current_width, current_height))
        
        # Adjust parameters for next iteration
        if current_quality > min_quality + 10:
            current_quality = max(current_quality - 15, min_quality)
        else:
            # Reduce dimensions if quality is already low
            current_width = max(int(current_width * step_factor), min_dimension)
            current_height = max(int(current_height * step_factor), min_dimension)
            current_quality = max_quality - 20
    
    # Return the best we could do
    if best_result:
        best_bytes, best_quality, best_dims = best_result
        info = CompressionInfo(
            success=False,
            final_size_kb=best_size / 1024,
            target_size_kb=target_kb,
            original_size_kb=original_size / 1024,
            quality=best_quality,
            dimensions=best_dims,
            original_dimensions=original_dims,
            iterations=max_iterations,
            note='Could not achieve target size, returning best effort',
        )
        return best_bytes, info
    
    raise ValueError(
        f"Could not compress image below {best_size / 1024:.1f}KB "
        f"(target: {target_kb}KB)"
    )


def _convert_to_rgb(img):
    """
    Convert image to RGB mode, handling transparency.
    
    Args:
        img: PIL Image object
    
    Returns:
        RGB Image object
    """
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create a white background for transparent images
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        mask = img.split()[-1] if img.mode == 'RGBA' else None
        background.paste(img, mask=mask)
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img