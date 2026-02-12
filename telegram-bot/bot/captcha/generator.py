"""
Generates a CAPTCHA image with random digits, noise lines, and dots.
Returns (BytesIO image, code_string).
"""

import io
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ── Colour palettes ─────────────────────────────────────────────────

BACKGROUNDS = [
    (240, 245, 250),  # light blue-gray
    (250, 245, 235),  # warm cream
    (235, 250, 240),  # mint
    (248, 240, 252),  # lavender
    (255, 248, 240),  # peach
]

TEXT_COLORS = [
    (30, 60, 120),
    (120, 30, 60),
    (20, 100, 60),
    (100, 40, 130),
    (50, 50, 50),
]

NOISE_COLORS = [
    (180, 200, 220),
    (200, 180, 190),
    (180, 210, 190),
    (210, 195, 220),
    (190, 190, 190),
]


def _random_color(palette: list[tuple]) -> tuple:
    return random.choice(palette)


def generate_captcha(length: int = 5, width: int = 280, height: int = 100) -> tuple[io.BytesIO, str]:
    """
    Generate a captcha image.

    Returns
    -------
    (image_bytes, code) — BytesIO PNG image and the correct code string.
    """
    code = "".join(str(random.randint(0, 9)) for _ in range(length))
    bg_color = _random_color(BACKGROUNDS)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # ── Try to use a built-in font; fall back to default ────────────
    font_size = 42
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # ── Draw noise lines (behind text) ──────────────────────────────
    for _ in range(random.randint(4, 7)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        line_color = _random_color(NOISE_COLORS)
        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=random.randint(1, 3))

    # ── Draw curved arcs ────────────────────────────────────────────
    for _ in range(random.randint(2, 4)):
        x1 = random.randint(-40, width // 2)
        y1 = random.randint(-40, height // 2)
        x2 = x1 + random.randint(80, width)
        y2 = y1 + random.randint(40, height)
        start_angle = random.randint(0, 360)
        end_angle = start_angle + random.randint(60, 180)
        arc_color = _random_color(NOISE_COLORS)
        draw.arc([(x1, y1), (x2, y2)], start_angle, end_angle, fill=arc_color, width=2)

    # ── Draw each digit with slight rotation and offset ─────────────
    total_text_width = length * 44
    x_start = (width - total_text_width) // 2

    for i, char in enumerate(code):
        char_img = Image.new("RGBA", (50, 60), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)

        text_color = _random_color(TEXT_COLORS)
        char_draw.text((5, 5), char, font=font, fill=text_color)

        angle = random.randint(-25, 25)
        char_img = char_img.rotate(angle, resample=Image.BICUBIC, expand=True)

        x_pos = x_start + i * 44 + random.randint(-3, 3)
        y_pos = (height - char_img.height) // 2 + random.randint(-8, 8)

        img.paste(char_img, (x_pos, y_pos), char_img)

    # ── Draw noise dots (on top) ────────────────────────────────────
    for _ in range(random.randint(100, 200)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        dot_color = _random_color(NOISE_COLORS)
        draw.ellipse([(x, y), (x + 2, y + 2)], fill=dot_color)

    # ── Apply slight blur ───────────────────────────────────────────
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))

    # ── Save to BytesIO ─────────────────────────────────────────────
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf, code
