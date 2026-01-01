"""Test helper utilities for common testing patterns."""
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
import zipfile
import io


def create_mock_image_url(index: int = 1) -> str:
    """Create a mock image URL for testing.
    
    Args:
        index: Optional index to make URLs unique
        
    Returns:
        Mock image URL string
    """
    return f"https://example.com/generated-image-{index}.png"


def create_mock_replicate_output(num_images: int = 1) -> List[str]:
    """Create mock Replicate API output.
    
    Args:
        num_images: Number of image URLs to generate
        
    Returns:
        List of mock image URLs
    """
    return [create_mock_image_url(i) for i in range(1, num_images + 1)]


def create_mock_streamlit_form_data(
    width: int = 1024,
    height: int = 1024,
    num_outputs: int = 1,
    scheduler: str = "DDIM",
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    prompt_strength: float = 0.8,
    refine: str = "expert_ensemble_refiner",
    high_noise_frac: float = 0.8,
    prompt: str = "test prompt",
    negative_prompt: str = "test negative prompt"
) -> Dict[str, Any]:
    """Create mock Streamlit form data for testing.
    
    Args:
        width: Image width
        height: Image height
        num_outputs: Number of output images
        scheduler: Scheduler type
        num_inference_steps: Number of inference steps
        guidance_scale: Guidance scale value
        prompt_strength: Prompt strength value
        refine: Refine style
        high_noise_frac: High noise fraction
        prompt: Text prompt
        negative_prompt: Negative text prompt
        
    Returns:
        Dictionary with form data
    """
    return {
        "width": width,
        "height": height,
        "num_outputs": num_outputs,
        "scheduler": scheduler,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "prompt_strength": prompt_strength,
        "refine": refine,
        "high_noise_frac": high_noise_frac,
        "prompt": prompt,
        "negative_prompt": negative_prompt
    }


def create_mock_zip_file(image_urls: List[str]) -> bytes:
    """Create a mock ZIP file containing images.
    
    Args:
        image_urls: List of image URLs to include in ZIP
        
    Returns:
        Bytes of ZIP file
    """
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for i, url in enumerate(image_urls):
            zipf.writestr(f"output_file_{i+1}.png", b'fake-image-data')
    zip_io.seek(0)
    return zip_io.getvalue()


def create_mock_streamlit_session_state(**kwargs) -> Dict[str, Any]:
    """Create a mock Streamlit session state dictionary.
    
    Args:
        **kwargs: Key-value pairs for session state
        
    Returns:
        Dictionary representing session state
    """
    default_state = {
        'model_configs': [],
        'selected_model': None,
        'generated_image': None,
        'all_images': []
    }
    default_state.update(kwargs)
    return default_state


def create_mock_replicate_error(error_type: str = "generic") -> Exception:
    """Create a mock Replicate API error.
    
    Args:
        error_type: Type of error ('generic', 'timeout', 'rate_limit', 'invalid_input')
        
    Returns:
        Exception instance
    """
    error_messages = {
        'generic': Exception("API Error"),
        'timeout': TimeoutError("Request timeout"),
        'rate_limit': Exception("Rate limit exceeded"),
        'invalid_input': ValueError("Invalid input parameters")
    }
    return error_messages.get(error_type, Exception("API Error"))


def create_mock_http_response(status_code: int = 200, content: bytes = b'fake-image-data') -> Mock:
    """Create a mock HTTP response.
    
    Args:
        status_code: HTTP status code
        content: Response content as bytes
        
    Returns:
        Mock response object
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.content = content
    mock_response.text = content.decode('utf-8', errors='ignore')
    return mock_response
