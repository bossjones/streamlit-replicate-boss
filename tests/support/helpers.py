"""Test helper utilities for common testing patterns."""
from typing import Dict, Any, List
from unittest.mock import Mock


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
