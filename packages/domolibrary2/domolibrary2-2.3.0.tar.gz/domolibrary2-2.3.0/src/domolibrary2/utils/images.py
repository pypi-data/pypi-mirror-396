"""
Image Processing Utilities

This module provides utilities for image processing, conversion, and manipulation.
Includes support for base64 encoding/decoding, image comparison, and various
image operations.

Functions:
    isBase64: Check if a string is valid base64
    handle_string_to_bytes_and_decode: Convert string/bytes to decoded bytes
    handle_string_to_bytes_and_encode: Convert string/bytes to base64 encoded bytes
    are_same_image: Compare two images for equality

Extended PIL.Image Methods:
    to_bytes: Convert PIL Image to bytes
    crop_square: Crop image to square aspect ratio
    from_image_file: Create PIL Image from file path (class method)
    from_bytestr: Create PIL Image from bytes/string (class method)

Example:
    >>> # Check if string is base64
    >>> is_valid = isBase64("SGVsbG8gV29ybGQ=")  # True

    >>> # Load image from file and crop to square
    >>> img = ImageUtils.from_image_file("photo.jpg")
    >>> square_img = img.crop_square()
    >>> img_bytes = img.to_bytes()

    >>> # Compare two images
    >>> img1 = ImageUtils.from_image_file("image1.jpg")
    >>> img2 = ImageUtils.from_image_file("image2.jpg")
    >>> same = are_same_image(img1, img2)

Note:
    Requires PIL (Pillow) and numpy for full functionality.
"""

import base64
import binascii
import io

import numpy as np
import PIL
from PIL import Image, UnidentifiedImageError

from .exceptions import ImageProcessingError

__all__ = [
    "isBase64",
    "Image",
    "handle_string_to_bytes_and_decode",
    "handle_string_to_bytes_and_encode",
    "are_same_image",
    "ImageUtils",
]


def isBase64(s: str | bytes) -> bool:
    """
    Check if a string or bytes object is valid base64.

    Args:
        s (Union[str, bytes]): String or bytes to check

    Returns:
        bool: True if input is valid base64, False otherwise

    Example:
        >>> isBase64("SGVsbG8gV29ybGQ=")  # "Hello World" in base64
        True
        >>> isBase64("not-base64!")
        False
        >>> isBase64(b"SGVsbG8gV29ybGQ=")
        True
    """
    try:
        if isinstance(s, str):
            s = s.encode("ascii")
        return base64.b64encode(base64.b64decode(s)) == s
    except (ValueError, binascii.Error):
        return False


def handle_string_to_bytes_and_decode(data: str | bytes) -> bytes:
    """
    Convert string or bytes to decoded bytes, handling base64 if present.

    Args:
        data (Union[str, bytes]): Data to convert and decode

    Returns:
        bytes: Decoded bytes data

    Example:
        >>> # Base64 encoded data gets decoded
        >>> decoded = handle_string_to_bytes_and_decode("SGVsbG8=")
        >>> print(decoded)  # b'Hello'

        >>> # Regular bytes pass through
        >>> decoded = handle_string_to_bytes_and_decode(b"Hello")
        >>> print(decoded)  # b'Hello'
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if isBase64(data):
        data = base64.b64decode(data)

    return data


def handle_string_to_bytes_and_encode(data: str | bytes) -> bytes:
    """
    Convert string or bytes to base64 encoded bytes.

    Args:
        data (Union[str, bytes]): Data to convert and encode

    Returns:
        bytes: Base64 encoded bytes

    Example:
        >>> # Raw bytes get base64 encoded
        >>> encoded = handle_string_to_bytes_and_encode(b"Hello")
        >>> print(encoded)  # b'SGVsbG8='

        >>> # Already base64 data passes through
        >>> encoded = handle_string_to_bytes_and_encode("SGVsbG8=")
        >>> print(encoded)  # b'SGVsbG8='
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if not isBase64(data):
        data = base64.b64encode(data)

    return data


def are_same_image(image1, image2) -> bool:
    """
    Compare two PIL Images to determine if they are identical.

    Uses PIL.ImageChops.difference to compare images pixel by pixel.

    Args:
        image1: First PIL Image to compare
        image2: Second PIL Image to compare

    Returns:
        bool: True if images are identical, False otherwise

    Raises:
        ImportError: If PIL or numpy are not available
        ImageProcessingError: If image comparison fails

    Example:
        >>> img1 = ImageUtils.from_image_file("image1.jpg")
        >>> img2 = ImageUtils.from_image_file("image2.jpg")
        >>> same = are_same_image(img1, img2)
        >>> print(same)  # True or False
    """

    try:
        img_chop = PIL.ImageChops.difference(image1, image2)
        pixel_sum = np.sum(np.array(img_chop.getdata()))
        print(f"Pixel difference sum: {pixel_sum}")
        return pixel_sum == 0

    except ValueError as e:
        print(f"Image comparison error: {e}")
        return False
    except (OSError, UnidentifiedImageError, RuntimeError) as e:
        raise ImageProcessingError("compare images", str(e)) from e


class ImageUtils:
    """
    Utility class providing extended functionality for PIL Images.

    This class provides static methods that extend PIL Image functionality
    without requiring monkey-patching of the PIL Image class.
    """

    @staticmethod
    def to_bytes(image, format_type: str = None) -> bytes:
        """
        Convert PIL Image to bytes.

        Args:
            image: PIL Image object
            format_type (str, optional): Image format (PNG, JPEG, etc.).
                                       If None, uses image's original format.

        Returns:
            bytes: Image data as bytes

        Raises:
            ImportError: If PIL is not available
            ImageProcessingError: If conversion fails

        Example:
            >>> img = ImageUtils.from_image_file("photo.jpg")
            >>> img_bytes = ImageUtils.to_bytes(img)
            >>> png_bytes = ImageUtils.to_bytes(img, "PNG")
        """

        try:
            byte_arr = io.BytesIO()
            save_format = format_type or getattr(image, "format", "PNG")
            image.save(byte_arr, format=save_format)
            return byte_arr.getvalue()

        except (OSError, ValueError, AttributeError) as e:
            raise ImageProcessingError("convert image to bytes", str(e)) from e

    @staticmethod
    def crop_square(image):
        """
        Crop image to square aspect ratio from center.

        Args:
            image: PIL Image object to crop

        Returns:
            PIL Image: Cropped square image

        Raises:
            ImportError: If PIL is not available
            ImageProcessingError: If cropping fails

        Example:
            >>> img = ImageUtils.from_image_file("rectangle.jpg")
            >>> square = ImageUtils.crop_square(img)
            >>> print(square.size)  # (min_dimension, min_dimension)
        """

        try:
            width, height = image.size
            new_edge = min(width, height)

            left = (width - new_edge) / 2
            top = (height - new_edge) / 2
            right = (width + new_edge) / 2
            bottom = (height + new_edge) / 2

            return image.crop((left, top, right, bottom))

        except (OSError, ValueError, AttributeError) as e:
            raise ImageProcessingError("crop image to square", str(e)) from e

    @classmethod
    def from_image_file(cls, image_path: str):
        """
        Create PIL Image from file path.

        Args:
            image_path (str): Path to image file

        Returns:
            PIL Image: Loaded image object

        Raises:
            ImportError: If PIL is not available
            FileNotFoundError: If image file doesn't exist
            ImageProcessingError: If image loading fails

        Example:
            >>> img = ImageUtils.from_image_file("/path/to/image.jpg")
            >>> print(img.size)  # (width, height)
        """

        try:
            with open(image_path, "rb") as file:
                data = file.read()

            data = handle_string_to_bytes_and_decode(data)
            return PIL.Image.open(io.BytesIO(data))

        except (OSError, ValueError, UnidentifiedImageError) as e:
            raise ImageProcessingError(
                f"load image from file {image_path}", str(e)
            ) from e

    @classmethod
    def from_bytestr(cls, data: str | bytes):
        """
        Create PIL Image from bytes or base64 string.

        Args:
            data (Union[str, bytes]): Image data as bytes or base64 string

        Returns:
            PIL Image: Loaded image object

        Raises:
            ImportError: If PIL is not available
            ImageProcessingError: If image loading fails

        Example:
            >>> # From bytes
            >>> with open("image.jpg", "rb") as f:
            ...     img_bytes = f.read()
            >>> img = ImageUtils.from_bytestr(img_bytes)

            >>> # From base64 string
            >>> base64_str = base64.b64encode(img_bytes).decode()
            >>> img = ImageUtils.from_bytestr(base64_str)
        """
        try:
            data = handle_string_to_bytes_and_decode(data)
            return PIL.Image.open(io.BytesIO(data))

        except (OSError, ValueError, UnidentifiedImageError) as e:
            raise ImageProcessingError("load image from bytes/string", str(e)) from e
