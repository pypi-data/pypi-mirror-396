"""
Pytest fixtures for semiautomatic tests.

Provides programmatically generated test images to avoid committing binary fixtures.
"""

import io
import pytest
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Pytest Configuration
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers and load environment."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API keys)"
    )
    # Load .env file for integration tests
    load_dotenv()


# ---------------------------------------------------------------------------
# Integration Test Output
# ---------------------------------------------------------------------------

@pytest.fixture
def integration_output_dir():
    """
    Provide directory for integration test outputs.

    Outputs are saved to tests/output/ for manual inspection.
    This directory is gitignored.
    """
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def small_rgb_image():
    """Create a small RGB test image (100x100, ~3KB as JPEG)."""
    img = Image.new('RGB', (100, 100), color=(255, 128, 64))
    # Add some variation to make it more realistic
    pixels = img.load()
    for x in range(100):
        for y in range(100):
            pixels[x, y] = ((x * 2) % 256, (y * 2) % 256, ((x + y) * 2) % 256)
    return img


@pytest.fixture
def large_rgb_image():
    """Create a larger RGB test image (2000x1500)."""
    img = Image.new('RGB', (2000, 1500), color=(100, 150, 200))
    pixels = img.load()
    for x in range(0, 2000, 10):
        for y in range(0, 1500, 10):
            pixels[x, y] = (255, 255, 255)
    return img


@pytest.fixture
def rgba_image():
    """Create an RGBA test image with transparency."""
    img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
    return img


@pytest.fixture
def small_image_path(temp_dir, small_rgb_image):
    """Save small test image to disk and return path."""
    path = temp_dir / "test_small.jpg"
    small_rgb_image.save(path, 'JPEG', quality=85)
    return path


@pytest.fixture
def large_image_path(temp_dir, large_rgb_image):
    """Save large test image to disk and return path."""
    path = temp_dir / "test_large.png"
    large_rgb_image.save(path, 'PNG')
    return path


@pytest.fixture
def rgba_image_path(temp_dir, rgba_image):
    """Save RGBA test image to disk and return path."""
    path = temp_dir / "test_rgba.png"
    rgba_image.save(path, 'PNG')
    return path


@pytest.fixture
def image_directory(temp_dir, small_rgb_image):
    """Create a directory structure with multiple test images."""
    # Root images
    (temp_dir / "image1.jpg").parent.mkdir(parents=True, exist_ok=True)
    small_rgb_image.save(temp_dir / "image1.jpg", 'JPEG')
    small_rgb_image.save(temp_dir / "image2.png", 'PNG')

    # Subdirectory
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    small_rgb_image.save(subdir / "image3.jpg", 'JPEG')

    # Non-image file (should be ignored)
    (temp_dir / "readme.txt").write_text("not an image")

    return temp_dir


@pytest.fixture
def oversized_image(temp_dir):
    """
    Create an image that will be larger than a small size limit.
    Uses high-entropy data to resist compression.
    """
    import random
    random.seed(42)  # Reproducible

    img = Image.new('RGB', (800, 600))
    pixels = img.load()
    for x in range(800):
        for y in range(600):
            pixels[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    path = temp_dir / "oversized.png"
    img.save(path, 'PNG')
    return path
