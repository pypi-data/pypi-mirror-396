#!/usr/bin/env python3
"""
ChromaSpec - Color Palette Analyzer

Extracts colors from SVG or image files (PNG, JPG, etc.) and generates a PDF
color swatch document organized by Red, Green, and Blue sections.

Usage:
    python chromaspec.py <input_file> [output.pdf]
    python chromaspec.py --help
"""

__version__ = "1.0.0"

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constants
HEX_COLOR_PATTERN = re.compile(r'#[0-9a-fA-F]{3,6}\b')
COLORS_PER_SECTION = 30
MARGIN = 0.5 * inch
RECT_HEIGHT = 0.25 * inch
RECT_WIDTH = 0.75 * inch
LABEL_SPACING = 0.1 * inch
SECTION_SPACING = 0.3 * inch
SECTION_HEADER_HEIGHT = 0.4 * inch
HEADER_HEIGHT = 0.4 * inch
FOOTER_HEIGHT = 0.3 * inch
PIE_RADIUS = 1.2 * inch
BAR_HEIGHT = 0.3 * inch
BAR_MAX_WIDTH = 4 * inch

# Supported file formats
SVG_EXTENSIONS = {'.svg'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
SUPPORTED_EXTENSIONS = SVG_EXTENSIONS | IMAGE_EXTENSIONS


def extract_hex_colors_from_svg(svg_content: str) -> Dict[str, float]:
    """
    Extract all HEX color values from SVG content with their frequencies.

    Args:
        svg_content: The SVG file content as a string.

    Returns:
        A dictionary mapping HEX color strings to their frequency percentages.
    """
    colors = HEX_COLOR_PATTERN.findall(svg_content)
    total = len(colors) if colors else 1
    color_counts = Counter(colors)
    return {color: (count / total) * 100 for color, count in color_counts.items()}


def extract_colors_from_image(image_path: Path, max_colors: int = 1000) -> Dict[str, float]:
    """
    Extract dominant colors from an image file with their frequencies.

    Args:
        image_path: Path to the image file.
        max_colors: Maximum number of colors to extract.

    Returns:
        A dictionary mapping HEX color strings to their frequency percentages.

    Raises:
        ImportError: If Pillow is not installed.
    """
    if not PIL_AVAILABLE:
        raise ImportError(
            "Pillow is required for image processing. "
            "Install it with: pip install Pillow"
        )

    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')

        max_dimension = 200
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension))

        pixels = list(img.getdata())
        total_pixels = len(pixels)
        color_counts = Counter(pixels)
        common_colors = color_counts.most_common(max_colors)

        hex_colors_with_freq = {
            f"#{r:02X}{g:02X}{b:02X}": (count / total_pixels) * 100
            for (r, g, b), count in common_colors
        }

        return hex_colors_with_freq


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert a HEX color string to an RGB tuple.

    Args:
        hex_color: A HEX color string (e.g., '#FF0000' or '#F00').

    Returns:
        A tuple of (red, green, blue) values (0-255).
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def rgb_to_cmyk(rgb: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
    """
    Convert an RGB tuple to CMYK values.

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        A tuple of (cyan, magenta, yellow, black) values (0-100).
    """
    r, g, b = rgb
    
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    k = 1 - max(r_norm, g_norm, b_norm)
    
    if k == 1:
        return (0, 0, 0, 100)
    
    c = (1 - r_norm - k) / (1 - k)
    m = (1 - g_norm - k) / (1 - k)
    y = (1 - b_norm - k) / (1 - k)
    
    return (
        round(c * 100),
        round(m * 100),
        round(y * 100),
        round(k * 100),
    )


def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Convert RGB to HSL (Hue, Saturation, Lightness).

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        A tuple of (hue 0-360, saturation 0-100, lightness 0-100).
    """
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2
    
    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    
    return (round(h * 360, 1), round(s * 100, 1), round(l * 100, 1))


def get_complementary_color(hex_color: str) -> str:
    """
    Get the complementary color (opposite on color wheel).

    Args:
        hex_color: A HEX color string.

    Returns:
        The complementary color as a HEX string.
    """
    rgb = hex_to_rgb(hex_color)
    comp = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
    return f"#{comp[0]:02X}{comp[1]:02X}{comp[2]:02X}"


def get_analogous_colors(hex_color: str) -> Tuple[str, str]:
    """
    Get analogous colors (adjacent on color wheel, ±30°).

    Args:
        hex_color: A HEX color string.

    Returns:
        A tuple of two analogous colors as HEX strings.
    """
    rgb = hex_to_rgb(hex_color)
    hsl = rgb_to_hsl(rgb)
    
    def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
        h /= 360
        s /= 100
        l /= 100
        
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p: float, q: float, t: float) -> float:
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return (round(r * 255), round(g * 255), round(b * 255))
    
    h1 = (hsl[0] + 30) % 360
    h2 = (hsl[0] - 30) % 360
    
    rgb1 = hsl_to_rgb(h1, hsl[1], hsl[2])
    rgb2 = hsl_to_rgb(h2, hsl[1], hsl[2])
    
    return (
        f"#{rgb1[0]:02X}{rgb1[1]:02X}{rgb1[2]:02X}",
        f"#{rgb2[0]:02X}{rgb2[1]:02X}{rgb2[2]:02X}"
    )


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance for WCAG contrast ratio.

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        Relative luminance value (0-1).
    """
    def adjust(c: int) -> float:
        c_norm = c / 255.0
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
    
    return 0.2126 * adjust(rgb[0]) + 0.7152 * adjust(rgb[1]) + 0.0722 * adjust(rgb[2])


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First HEX color string.
        color2: Second HEX color string.

    Returns:
        Contrast ratio (1-21).
    """
    l1 = calculate_luminance(hex_to_rgb(color1))
    l2 = calculate_luminance(hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_wcag_rating(contrast_ratio: float) -> str:
    """
    Get WCAG accessibility rating based on contrast ratio.

    Args:
        contrast_ratio: The contrast ratio value.

    Returns:
        WCAG rating string (AAA, AA, or Fail).
    """
    if contrast_ratio >= 7:
        return "AAA"
    elif contrast_ratio >= 4.5:
        return "AA"
    elif contrast_ratio >= 3:
        return "AA Large"
    return "Fail"


def is_red_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of red.

    A color is considered red if the red component is greater than
    both the green and blue components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of red, False otherwise.
    """
    red, green, blue = rgb
    return red > max(green, blue)


def is_green_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of green.

    A color is considered green if the green component is greater than
    both the red and blue components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of green, False otherwise.
    """
    red, green, blue = rgb
    return green > max(red, blue)


def is_blue_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of blue.

    A color is considered blue if the blue component is greater than
    both the red and green components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of blue, False otherwise.
    """
    red, green, blue = rgb
    return blue > max(red, green)


def filter_blue_colors(hex_colors: List[str]) -> List[str]:
    """
    Filter a list of HEX colors to return only blue shades.

    Args:
        hex_colors: A list of HEX color strings.

    Returns:
        A sorted list of unique blue HEX color strings.
    """
    blue_colors = {
        color for color in hex_colors
        if is_blue_color(hex_to_rgb(color))
    }
    return sorted(blue_colors)


def categorize_colors(hex_colors_with_freq: Dict[str, float]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Categorize colors into Red, Green, and Blue groups with frequencies.

    Args:
        hex_colors_with_freq: A dictionary mapping HEX colors to frequency percentages.

    Returns:
        A dictionary with 'red', 'green', 'blue' keys containing lists of (color, frequency) tuples.
    """
    categories: Dict[str, List[Tuple[str, float]]] = {
        'red': [],
        'green': [],
        'blue': [],
    }

    for color, freq in hex_colors_with_freq.items():
        rgb = hex_to_rgb(color)
        if is_red_color(rgb):
            categories['red'].append((color, freq))
        elif is_green_color(rgb):
            categories['green'].append((color, freq))
        elif is_blue_color(rgb):
            categories['blue'].append((color, freq))

    for key in categories:
        categories[key] = sorted(categories[key], key=lambda x: x[1], reverse=True)

    return categories


def draw_header(pdf: canvas.Canvas, width: float, height: float) -> None:
    """
    Draw a header on the current page.

    Args:
        pdf: The canvas object.
        width: Page width.
        height: Page height.
    """
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, height - MARGIN / 2, "ChromaSpec Report")
    pdf.setStrokeColor("gray")
    pdf.line(MARGIN, height - MARGIN + 0.1 * inch, width - MARGIN, height - MARGIN + 0.1 * inch)


def draw_footer(pdf: canvas.Canvas, width: float, page_number: int) -> None:
    """
    Draw a footer on the current page.

    Args:
        pdf: The canvas object.
        width: Page width.
        page_number: Current page number.
    """
    pdf.setFont("Courier", 8)
    pdf.setFillColor("gray")
    pdf.setStrokeColor("gray")
    pdf.line(MARGIN, FOOTER_HEIGHT, width - MARGIN, FOOTER_HEIGHT)
    pdf.drawRightString(width - MARGIN, FOOTER_HEIGHT - 0.15 * inch, f"Page {page_number}")
    pdf.drawString(MARGIN, FOOTER_HEIGHT - 0.15 * inch, "Generated by ChromaSpec")


def draw_cover_page(pdf: canvas.Canvas, input_path: Path, color_categories: Dict[str, List[Tuple[str, float]]], width: float, height: float) -> None:
    """
    Draw the cover page with image preview and summary.

    Args:
        pdf: The canvas object.
        input_path: Path to the input image file.
        color_categories: Dictionary with color categories.
        width: Page width.
        height: Page height.
    """
    # Title
    pdf.setFont("Courier-Bold", 24)
    pdf.setFillColor("black")
    title = "ChromaSpec"
    title_width = pdf.stringWidth(title, "Courier-Bold", 24)
    pdf.drawString((width - title_width) / 2, height - 1 * inch, title)

    # Subtitle with filename
    pdf.setFont("Courier", 12)
    pdf.setFillColor("gray")
    subtitle = f"Color analysis for: {input_path.name}"
    subtitle_width = pdf.stringWidth(subtitle, "Courier", 12)
    pdf.drawString((width - subtitle_width) / 2, height - 1.4 * inch, subtitle)

    # Draw the image if it's an image file (not SVG)
    y_after_image = height - 1.8 * inch
    if input_path.suffix.lower() in IMAGE_EXTENSIONS and PIL_AVAILABLE:
        try:
            with Image.open(input_path) as img:
                # Calculate image dimensions to fit on page
                max_img_width = width - 2 * MARGIN
                max_img_height = 4 * inch
                
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                
                if img_width > max_img_width:
                    img_width = max_img_width
                    img_height = img_width / aspect_ratio
                
                if img_height > max_img_height:
                    img_height = max_img_height
                    img_width = img_height * aspect_ratio
                
                # Center the image
                x_pos = (width - img_width) / 2
                y_pos = height - 2 * inch - img_height
                
                # Draw image
                pdf.drawImage(
                    str(input_path),
                    x_pos, y_pos,
                    width=img_width, height=img_height,
                    preserveAspectRatio=True
                )
                y_after_image = y_pos - 0.5 * inch
        except Exception:
            # If image can't be loaded, just skip it
            pass

    # Summary statistics
    total_red = len(color_categories['red'])
    total_green = len(color_categories['green'])
    total_blue = len(color_categories['blue'])
    total_colors = total_red + total_green + total_blue

    pdf.setFont("Courier-Bold", 14)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y_after_image, "Color Summary")

    pdf.setFont("Courier", 12)
    y_after_image -= 0.4 * inch
    pdf.drawString(MARGIN, y_after_image, f"Total colors extracted: {total_colors}")
    y_after_image -= 0.3 * inch
    pdf.setFillColor("#CC0000")
    pdf.drawString(MARGIN, y_after_image, f"Red colors:   {total_red}")
    y_after_image -= 0.3 * inch
    pdf.setFillColor("#00CC00")
    pdf.drawString(MARGIN, y_after_image, f"Green colors: {total_green}")
    y_after_image -= 0.3 * inch
    pdf.setFillColor("#0000CC")
    pdf.drawString(MARGIN, y_after_image, f"Blue colors:  {total_blue}")

    draw_footer(pdf, width, 1)


def draw_section_header(pdf: canvas.Canvas, title: str, y_position: float) -> float:
    """
    Draw a section header in the PDF.

    Args:
        pdf: The canvas object.
        title: The section title.
        y_position: Current Y position.

    Returns:
        Updated Y position after the header.
    """
    pdf.setFont("Courier-Bold", 14)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y_position - SECTION_HEADER_HEIGHT / 2, title)
    pdf.setFont("Courier", 10)
    return y_position - SECTION_HEADER_HEIGHT


def draw_pie_chart(pdf: canvas.Canvas, color_categories: Dict[str, List[Tuple[str, float]]], 
                   center_x: float, center_y: float, radius: float) -> None:
    """
    Draw a pie chart showing RGB distribution.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        center_x: X coordinate of pie center.
        center_y: Y coordinate of pie center.
        radius: Radius of the pie chart.
    """
    total_red = len(color_categories['red'])
    total_green = len(color_categories['green'])
    total_blue = len(color_categories['blue'])
    total = total_red + total_green + total_blue
    
    if total == 0:
        return
    
    colors_data = [
        ('#E74C3C', total_red / total * 360, 'Red'),
        ('#2ECC71', total_green / total * 360, 'Green'),
        ('#3498DB', total_blue / total * 360, 'Blue'),
    ]
    
    start_angle = 90
    for color, angle, _ in colors_data:
        if angle > 0:
            pdf.setFillColor(color)
            pdf.setStrokeColor(color)
            pdf.wedge(center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius,
                     start_angle, angle, fill=1, stroke=0)
            start_angle += angle


def draw_bar_chart(pdf: canvas.Canvas, color_categories: Dict[str, List[Tuple[str, float]]], 
                   x: float, y: float, max_width: float) -> float:
    """
    Draw horizontal bar chart showing color distribution.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        x: Starting X position.
        y: Starting Y position.
        max_width: Maximum bar width.

    Returns:
        Updated Y position after the chart.
    """
    total_red = len(color_categories['red'])
    total_green = len(color_categories['green'])
    total_blue = len(color_categories['blue'])
    total = max(total_red, total_green, total_blue, 1)
    
    bars = [
        ('#E74C3C', total_red, 'Red'),
        ('#2ECC71', total_green, 'Green'),
        ('#3498DB', total_blue, 'Blue'),
    ]
    
    pdf.setFont("Courier", 10)
    for color, count, label in bars:
        bar_width = (count / total) * max_width if total > 0 else 0
        
        pdf.setFillColor("black")
        pdf.drawString(x, y - BAR_HEIGHT / 2 - 3, f"{label}:")
        
        if bar_width > 0:
            pdf.setFillColor(color)
            pdf.rect(x + 0.6 * inch, y - BAR_HEIGHT, bar_width, BAR_HEIGHT, fill=1, stroke=0)
        
        pdf.setFillColor("black")
        pdf.drawString(x + 0.6 * inch + bar_width + 0.1 * inch, y - BAR_HEIGHT / 2 - 3, str(count))
        
        y -= BAR_HEIGHT + 0.15 * inch
    
    return y


def draw_statistics_page(pdf: canvas.Canvas, color_categories: Dict[str, List[Tuple[str, float]]], 
                         width: float, height: float, page_number: int) -> None:
    """
    Draw a statistics and visualization page.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        width: Page width.
        height: Page height.
        page_number: Current page number.
    """
    draw_header(pdf, width, height)
    draw_footer(pdf, width, page_number)
    
    y = height - MARGIN - HEADER_HEIGHT - 0.3 * inch
    
    pdf.setFont("Courier-Bold", 16)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y, "Color Distribution")
    y -= 0.5 * inch
    
    pie_center_x = MARGIN + PIE_RADIUS + 0.3 * inch
    pie_center_y = y - PIE_RADIUS
    draw_pie_chart(pdf, color_categories, pie_center_x, pie_center_y, PIE_RADIUS)
    
    legend_x = pie_center_x + PIE_RADIUS + 0.5 * inch
    legend_y = y - 0.3 * inch
    
    total_red = len(color_categories['red'])
    total_green = len(color_categories['green'])
    total_blue = len(color_categories['blue'])
    total = total_red + total_green + total_blue
    
    legend_items = [
        ('#E74C3C', 'Red', total_red, total_red / total * 100 if total > 0 else 0),
        ('#2ECC71', 'Green', total_green, total_green / total * 100 if total > 0 else 0),
        ('#3498DB', 'Blue', total_blue, total_blue / total * 100 if total > 0 else 0),
    ]
    
    pdf.setFont("Courier", 10)
    for color, label, count, pct in legend_items:
        pdf.setFillColor(color)
        pdf.rect(legend_x, legend_y - 0.12 * inch, 0.15 * inch, 0.15 * inch, fill=1, stroke=0)
        pdf.setFillColor("black")
        pdf.drawString(legend_x + 0.25 * inch, legend_y - 0.12 * inch, f"{label}: {count} ({pct:.1f}%)")
        legend_y -= 0.35 * inch
    
    y = pie_center_y - PIE_RADIUS - 0.6 * inch
    
    pdf.setFont("Courier-Bold", 14)
    pdf.drawString(MARGIN, y, "Color Count Comparison")
    y -= 0.4 * inch
    
    y = draw_bar_chart(pdf, color_categories, MARGIN, y, BAR_MAX_WIDTH)


def draw_top_colors_page(pdf: canvas.Canvas, color_categories: Dict[str, List[Tuple[str, float]]], 
                         width: float, height: float, page_number: int) -> None:
    """
    Draw a page with top colors and their harmonies.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        width: Page width.
        height: Page height.
        page_number: Current page number.
    """
    draw_header(pdf, width, height)
    draw_footer(pdf, width, page_number)
    
    y = height - MARGIN - HEADER_HEIGHT - 0.3 * inch
    
    pdf.setFont("Courier-Bold", 16)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y, "Top Colors & Harmonies")
    y -= 0.5 * inch
    
    all_colors = []
    for section_key in ['red', 'green', 'blue']:
        all_colors.extend(color_categories[section_key])
    
    top_colors = sorted(all_colors, key=lambda x: x[1], reverse=True)[:5]
    
    for i, (color, freq) in enumerate(top_colors, 1):
        pdf.setFont("Courier-Bold", 12)
        pdf.setFillColor("black")
        pdf.drawString(MARGIN, y, f"#{i} Most Used Color ({freq:.2f}%)")
        y -= 0.35 * inch
        
        box_size = 0.4 * inch
        pdf.setFillColor(color)
        pdf.rect(MARGIN, y - box_size, box_size, box_size, fill=1, stroke=0)
        
        rgb = hex_to_rgb(color)
        hsl = rgb_to_hsl(rgb)
        
        pdf.setFont("Courier", 9)
        pdf.setFillColor("black")
        info_x = MARGIN + box_size + 0.15 * inch
        pdf.drawString(info_x, y - 0.12 * inch, f"HEX: {color.upper()}")
        pdf.drawString(info_x, y - 0.24 * inch, f"HSL: {hsl[0]}°, {hsl[1]}%, {hsl[2]}%")
        
        comp_color = get_complementary_color(color)
        pdf.drawString(info_x + 2.2 * inch, y - 0.12 * inch, "Complementary:")
        pdf.setFillColor(comp_color)
        pdf.rect(info_x + 3.5 * inch, y - 0.22 * inch, 0.25 * inch, 0.25 * inch, fill=1, stroke=0)
        
        analog1, analog2 = get_analogous_colors(color)
        pdf.setFillColor("black")
        pdf.drawString(info_x + 2.2 * inch, y - 0.35 * inch, "Analogous:")
        pdf.setFillColor(analog1)
        pdf.rect(info_x + 3.5 * inch, y - 0.45 * inch, 0.25 * inch, 0.25 * inch, fill=1, stroke=0)
        pdf.setFillColor(analog2)
        pdf.rect(info_x + 3.75 * inch, y - 0.45 * inch, 0.25 * inch, 0.25 * inch, fill=1, stroke=0)
        
        y -= box_size + 0.35 * inch


def draw_accessibility_page(pdf: canvas.Canvas, color_categories: Dict[str, List[Tuple[str, float]]], 
                            width: float, height: float, page_number: int) -> None:
    """
    Draw a page with accessibility/contrast information.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        width: Page width.
        height: Page height.
        page_number: Current page number.
    """
    draw_header(pdf, width, height)
    draw_footer(pdf, width, page_number)
    
    y = height - MARGIN - HEADER_HEIGHT - 0.3 * inch
    
    pdf.setFont("Courier-Bold", 16)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y, "Accessibility & Contrast")
    y -= 0.4 * inch
    
    pdf.setFont("Courier", 10)
    pdf.setFillColor("gray")
    pdf.drawString(MARGIN, y, "WCAG 2.1 contrast ratios for text readability")
    y -= 0.5 * inch
    
    all_colors = []
    for section_key in ['red', 'green', 'blue']:
        all_colors.extend(color_categories[section_key])
    
    top_colors = sorted(all_colors, key=lambda x: x[1], reverse=True)[:8]
    
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor("black")
    col1 = MARGIN
    col2 = MARGIN + 1.5 * inch
    col3 = MARGIN + 3.0 * inch
    col4 = MARGIN + 4.5 * inch
    pdf.drawString(col1, y, "Color")
    pdf.drawString(col2, y, "vs White")
    pdf.drawString(col3, y, "vs Black")
    pdf.drawString(col4, y, "Best Use")
    y -= 0.35 * inch
    
    pdf.setStrokeColor("gray")
    pdf.line(MARGIN, y + 0.1 * inch, width - MARGIN, y + 0.1 * inch)
    y -= 0.15 * inch
    
    for color, freq in top_colors:
        box_size = 0.25 * inch
        pdf.setFillColor(color)
        pdf.rect(MARGIN, y - box_size, box_size, box_size, fill=1, stroke=0)
        
        pdf.setFont("Courier", 9)
        pdf.setFillColor("black")
        pdf.drawString(MARGIN + box_size + 0.1 * inch, y - box_size / 2 - 3, color.upper())
        
        ratio_white = get_contrast_ratio(color, "#FFFFFF")
        ratio_black = get_contrast_ratio(color, "#000000")
        
        rating_white = get_wcag_rating(ratio_white)
        rating_black = get_wcag_rating(ratio_black)
        
        if rating_white in ["AAA", "AA"]:
            pdf.setFillColor("#2ECC71")
        elif rating_white == "AA Large":
            pdf.setFillColor("#F39C12")
        else:
            pdf.setFillColor("#E74C3C")
        pdf.drawString(col2, y - box_size / 2 - 3, f"{ratio_white:.1f}:1 ({rating_white})")
        
        if rating_black in ["AAA", "AA"]:
            pdf.setFillColor("#2ECC71")
        elif rating_black == "AA Large":
            pdf.setFillColor("#F39C12")
        else:
            pdf.setFillColor("#E74C3C")
        pdf.drawString(col3, y - box_size / 2 - 3, f"{ratio_black:.1f}:1 ({rating_black})")
        
        pdf.setFillColor("black")
        if ratio_white > ratio_black:
            best_use = "White text on color"
        else:
            best_use = "Black text on color"
        pdf.drawString(col4, y - box_size / 2 - 3, best_use)
        
        y -= box_size + 0.2 * inch
    
    y -= 0.3 * inch
    pdf.setFont("Courier-Bold", 10)
    pdf.setFillColor("black")
    pdf.drawString(MARGIN, y, "WCAG Rating Guide:")
    y -= 0.25 * inch
    pdf.setFont("Courier", 9)
    pdf.setFillColor("#2ECC71")
    pdf.drawString(MARGIN, y, "AAA (≥7:1) - Excellent for all text")
    y -= 0.2 * inch
    pdf.setFillColor("#2ECC71")
    pdf.drawString(MARGIN, y, "AA (≥4.5:1) - Good for normal text")
    y -= 0.2 * inch
    pdf.setFillColor("#F39C12")
    pdf.drawString(MARGIN, y, "AA Large (≥3:1) - OK for large text only")
    y -= 0.2 * inch
    pdf.setFillColor("#E74C3C")
    pdf.drawString(MARGIN, y, "Fail (<3:1) - Not accessible")


def generate_color_pdf(output_path: Path, color_categories: Dict[str, List[Tuple[str, float]]], input_path: Path) -> None:
    """
    Generate a PDF document with color swatches organized by RGB sections.

    Args:
        output_path: The path for the output PDF file.
        color_categories: Dictionary with 'red', 'green', 'blue' keys containing (color, frequency) tuples.
        input_path: Path to the original input file (for cover page).
    """
    total_colors = sum(len(colors) for colors in color_categories.values())
    if total_colors == 0:
        print("No colors to write to PDF.")
        return

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    page_number = 1

    draw_cover_page(pdf, input_path, color_categories, width, height)
    pdf.showPage()
    page_number += 1

    draw_statistics_page(pdf, color_categories, width, height, page_number)
    pdf.showPage()
    page_number += 1

    draw_top_colors_page(pdf, color_categories, width, height, page_number)
    pdf.showPage()
    page_number += 1

    draw_accessibility_page(pdf, color_categories, width, height, page_number)
    pdf.showPage()
    page_number += 1

    y_position = height - MARGIN - HEADER_HEIGHT

    section_titles = {
        'red': 'Red Colors',
        'green': 'Green Colors',
        'blue': 'Blue Colors',
    }

    draw_header(pdf, width, height)
    draw_footer(pdf, width, page_number)

    for section_key in ['red', 'green', 'blue']:
        colors = color_categories[section_key]
        if not colors:
            continue

        if y_position < MARGIN + FOOTER_HEIGHT + SECTION_HEADER_HEIGHT + RECT_HEIGHT:
            pdf.showPage()
            page_number += 1
            draw_header(pdf, width, height)
            draw_footer(pdf, width, page_number)
            y_position = height - MARGIN - HEADER_HEIGHT

        y_position = draw_section_header(pdf, section_titles[section_key], y_position)

        for color, frequency in colors:
            if y_position < MARGIN + FOOTER_HEIGHT + RECT_HEIGHT:
                pdf.showPage()
                page_number += 1
                draw_header(pdf, width, height)
                draw_footer(pdf, width, page_number)
                y_position = height - MARGIN - HEADER_HEIGHT

            pdf.setFillColor(color)
            pdf.setStrokeColor(color)
            pdf.rect(MARGIN, y_position - RECT_HEIGHT, RECT_WIDTH, RECT_HEIGHT, fill=1, stroke=0)

            rgb = hex_to_rgb(color)
            cmyk = rgb_to_cmyk(rgb)

            pdf.setFont("Courier", 10)
            pdf.setFillColor("black")
            label = f"{color.upper()}  RGB({rgb[0]:3},{rgb[1]:3},{rgb[2]:3})  CMYK({cmyk[0]:3},{cmyk[1]:3},{cmyk[2]:3},{cmyk[3]:3})  {frequency:.3f}%"
            text_y = y_position - RECT_HEIGHT / 2 - 3.5
            pdf.drawString(
                MARGIN + RECT_WIDTH + LABEL_SPACING,
                text_y,
                label
            )

            y_position -= RECT_HEIGHT

        y_position -= SECTION_SPACING

    pdf.showPage()
    pdf.save()
    print(f"PDF saved to: {output_path}")


def extract_colors(input_path: Path) -> Dict[str, float]:
    """
    Extract colors from an input file (SVG or image) with frequencies.

    Args:
        input_path: Path to the input file.

    Returns:
        A dictionary mapping HEX color strings to frequency percentages.

    Raises:
        ValueError: If the file format is not supported.
    """
    extension = input_path.suffix.lower()

    if extension in SVG_EXTENSIONS:
        svg_content = input_path.read_text(encoding='utf-8')
        return extract_hex_colors_from_svg(svg_content)
    elif extension in IMAGE_EXTENSIONS:
        return extract_colors_from_image(input_path)
    else:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def process_file(input_path: Path, output_path: Path) -> None:
    """
    Process an input file to extract colors and generate a PDF.

    Args:
        input_path: Path to the input file (SVG or image).
        output_path: Path for the output PDF file.

    Raises:
        FileNotFoundError: If the input file doesn't exist.
        ValueError: If no colors are found.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    hex_colors_with_freq = extract_colors(input_path)
    color_categories = categorize_colors(hex_colors_with_freq)

    total_colors = sum(len(colors) for colors in color_categories.values())
    if total_colors == 0:
        raise ValueError(f"No red, green, or blue colors found in {input_path}")

    print(f"Found colors - Red: {len(color_categories['red'])}, "
          f"Green: {len(color_categories['green'])}, "
          f"Blue: {len(color_categories['blue'])}")

    generate_color_pdf(output_path, color_categories, input_path)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    supported_formats = ', '.join(sorted(SUPPORTED_EXTENSIONS))
    parser = argparse.ArgumentParser(
        description="Extract colors from SVG or image files and generate a PDF color swatch organized by Red, Green, and Blue sections.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported formats: {supported_formats}

Examples:
    %(prog)s image.svg
    %(prog)s photo.png
    %(prog)s image.jpg custom_output.pdf
        """,
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help=f"Path to the input file ({supported_formats})",
    )
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",
        default=None,
        help="Path for the output PDF file (default: <input_name>_colors.pdf)",
    )
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_arguments()

    extension = args.input_file.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        print(
            f"Error: Unsupported file format '{extension}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            file=sys.stderr
        )
        return 1

    if extension in IMAGE_EXTENSIONS and not PIL_AVAILABLE:
        print(
            "Error: Pillow is required for image processing. "
            "Install it with: pip install Pillow",
            file=sys.stderr
        )
        return 1

    output_path = args.output_pdf
    if output_path is None:
        output_path = args.input_file.with_name(
            f"{args.input_file.stem}_colors.pdf"
        )

    try:
        process_file(args.input_file, output_path)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Warning: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())