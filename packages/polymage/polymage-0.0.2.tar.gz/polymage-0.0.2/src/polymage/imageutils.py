import base64
from io import BytesIO
from PIL import Image


def base64_to_image(base64_string) -> Image.Image:
    """
    Convert a base64 string to a PIL Image object.
    
    Args:
        base64_string (str): Base64 encoded image string
        
    Returns:
        PIL.Image.Image: The decoded image as a PIL Image object
        
    Raises:
        ValueError: If the base64 string is invalid or cannot be decoded
        OSError: If the decoded data is not a valid image format
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if base64_string.startswith('data:'):
            # Find the comma and take everything after it
            base64_string = base64_string.split(',', 1)[1]
        
        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Create a BytesIO object from the decoded bytes
        image_buffer = BytesIO(image_bytes)
        
        # Open the image using PIL
        image = Image.open(image_buffer)
        
        # Load the image data to ensure it's valid
        image.load()
        
        return image

    except OSError as e:
        raise OSError(f"Invalid image data or unsupported format: {e}")


def image_to_base64(image, format='PNG') -> str:
    """
    Convert an image to a base64-encoded string.

    Parameters:
        image (str or PIL.Image.Image): 
            - If str: path to the image file.
            - If PIL.Image.Image: an in-memory image object.
        format (str): 
            The image format to use when encoding (e.g., 'PNG', 'JPEG'). 
            Only used if input is a PIL Image object. Default is 'PNG'.

    Returns:
        str: Base64-encoded string of the image.

    Raises:
        FileNotFoundError: If image path does not exist.
        ValueError: If input type is not supported.
    """
    if isinstance(image, str):
        # Input is a file path
        with open(image, "rb") as image_file:
            encoded_str = base64.b64encode(image_file.read()).decode('utf-8')
    elif isinstance(image, Image.Image):
        # Input is a PIL Image object
        buffered = BytesIO()
        image.save(buffered, format=format)
        encoded_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    else:
        raise ValueError("Input must be a file path (str) or a PIL Image object.")

    return encoded_str
