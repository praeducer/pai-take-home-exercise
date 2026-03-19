import io

from PIL import Image

from src.pipeline.text_overlay import apply_overlay

CONTENT = {
    "title": "Test Product\nOriginal",
    "attributes": ["organic", "non-gmo"],
    "regulatory_text": "Contains: nuts. See label.",
}


def _make_image(width: int, height: int) -> bytes:
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_overlay_returns_bytes():
    image_bytes = _make_image(1024, 1024)
    result = apply_overlay(image_bytes, CONTENT, "1:1")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_overlay_larger_than_input():
    image_bytes = _make_image(1024, 1024)
    result = apply_overlay(image_bytes, CONTENT, "1:1")
    assert len(result) > len(image_bytes)


def test_overlay_correct_dimensions_square():
    image_bytes = _make_image(1024, 1024)
    result = apply_overlay(image_bytes, CONTENT, "1:1")
    result_img = Image.open(io.BytesIO(result))
    assert result_img.size == (1024, 1024)


def test_overlay_correct_dimensions_portrait():
    image_bytes = _make_image(576, 1024)
    result = apply_overlay(image_bytes, CONTENT, "9:16")
    result_img = Image.open(io.BytesIO(result))
    assert result_img.size == (576, 1024)


def test_overlay_correct_dimensions_landscape():
    image_bytes = _make_image(1024, 576)
    result = apply_overlay(image_bytes, CONTENT, "16:9")
    result_img = Image.open(io.BytesIO(result))
    assert result_img.size == (1024, 576)


def test_overlay_all_ratios_succeed():
    for ratio, size in [("1:1", (1024, 1024)), ("9:16", (576, 1024)), ("16:9", (1024, 576))]:
        image_bytes = _make_image(*size)
        result = apply_overlay(image_bytes, CONTENT, ratio)
        assert len(result) > 0, f"Empty result for ratio {ratio}"


def test_overlay_empty_attributes():
    content = {**CONTENT, "attributes": []}
    image_bytes = _make_image(1024, 1024)
    result = apply_overlay(image_bytes, content, "1:1")
    assert len(result) > 0
