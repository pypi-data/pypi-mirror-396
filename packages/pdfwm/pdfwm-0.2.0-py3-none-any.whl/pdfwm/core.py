"""Core functionality for PDF watermarking."""

import io
import shutil
from typing import Optional, Tuple
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


def _parse_hex_color(hex_color: str) -> Color:
  """Parse hex color string (RGB or RGBA) and return Color object.

  Args:
      hex_color: Hex color string like '#808080', '#80808019', '808080', or '80808019'

  Returns:
      Color object with RGB values (0-1) and alpha (0-1)

  Raises:
      ValueError: If hex_color is not 6 or 8 characters
  """
  # Remove '#' if present
  hex_color = hex_color.lstrip('#')

  # Validate hex string length
  if len(hex_color) not in (6, 8):
    raise ValueError(
      f"Invalid hex color: must be 6 (RGB) or 8 (RGBA) characters, got {len(hex_color)}")

  # Parse RGB values
  r = int(hex_color[0:2], 16) / 255.0
  g = int(hex_color[2:4], 16) / 255.0
  b = int(hex_color[4:6], 16) / 255.0

  # Parse alpha if provided, otherwise default to 0.15 (15%)
  if len(hex_color) == 8:
    alpha = int(hex_color[6:8], 16) / 255.0
  else:
    alpha = 0.15

  return Color(r, g, b, alpha=alpha)


def _create_watermark(
    text: str,
    width: float,
    height: float,
    color: Optional[str] = None
) -> PdfReader:
  """Create a PDF with the watermark text.

  Args:
      text: Text to use as watermark
      width: Page width in points
      height: Page height in points
      color: Hex color string (RGB or RGBA). If None, uses 50% gray with 15% opacity

  Returns:
      PdfReader object containing the watermark
  """
  packet = io.BytesIO()
  can = canvas.Canvas(packet, pagesize=(width, height))

  # Text configuration: use provided color or default to 50% gray, 15% opacity.
  if color is None:
    color_obj = Color(0.5, 0.5, 0.5, alpha=0.15)
  else:
    color_obj = _parse_hex_color(color)
  can.setFillColor(color_obj)

  # Calculate the maximum font size so the text fits within the width.
  # With a 45° rotation, the usable diagonal is approximately min(width, height).
  max_width = min(width, height)
  font_name = "Helvetica-Bold"

  # Binary search to find the maximum size.
  min_size = 10
  max_size = 300
  optimal_size = min_size

  while max_size - min_size > 1:
    test_size = (min_size + max_size) / 2
    text_width = can.stringWidth(text, font_name, test_size)
    if text_width <= max_width:
      optimal_size = test_size
      min_size = test_size
    else:
      max_size = test_size

  # Optimal font and size.
  can.setFont(font_name, optimal_size)

  # Save state and rotate 45 degrees.
  can.saveState()
  can.translate(width / 2, height / 2)
  can.rotate(45)

  # Center the text.
  text_width = can.stringWidth(text, font_name, optimal_size)
  can.drawString(-text_width / 2, 0, text)

  can.restoreState()
  can.save()

  packet.seek(0)
  return PdfReader(packet)


def process_pdf(
    input_path: str,
    output_path: str,
    watermark_text: str,
    watermark_color: Optional[str] = None,
    overwrite: bool = False
) -> Tuple[bool, str]:
  """Process a single PDF file with watermark.

  Args:
      input_path: Path to input PDF file
      output_path: Path to output PDF file (or temp file for overwrite mode)
      watermark_text: Text to use as watermark
      watermark_color: Hex color string (RGB or RGBA). If None, uses default 50% gray with 15% opacity
      overwrite: Whether this is overwrite mode

  Returns:
      Tuple of (success: bool, message: str)
  """
  try:
    # Read input PDF
    try:
      input_pdf = PdfReader(input_path)
    except PdfReadError as e:
      return (False, f'Invalid or corrupted PDF file: {e}')
    except Exception as e:
      return (False, f'Failed to read PDF file: {e}')

    output_pdf = PdfWriter()

    # Process each page
    page_count = len(input_pdf.pages)
    if page_count == 0:
      return (False, 'PDF file has no pages')

    for i in range(page_count):
      try:
        page = input_pdf.pages[i]

        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        # Validate page dimensions
        if page_width <= 0 or page_height <= 0:
          continue

        # Create watermark for this page
        watermark = _create_watermark(
          watermark_text, page_width, page_height, watermark_color)
        watermark_first_page = watermark.pages[0]

        # Merge watermark with page
        page.merge_page(watermark_first_page)
        output_pdf.add_page(page)
      except Exception:
        # Skip problematic pages
        continue

    if len(output_pdf.pages) == 0:
      return (False, 'No pages were successfully processed')

    # Write output PDF
    try:
      with open(output_path, 'wb') as output_file:
        output_pdf.write(output_file)
    except PermissionError:
      return (False, f'Permission denied to write output file')
    except IOError as e:
      return (False, f'Failed to write output file (check disk space): {e}')
    except Exception as e:
      return (False, f'Failed to write PDF file: {e}')

    # If overwrite mode, replace the original file
    if overwrite:
      try:
        shutil.move(output_path, input_path)
      except Exception as e:
        return (False, f'Failed to overwrite original file: {e}')

    return (True, f'Successfully processed {len(output_pdf.pages)} page(s)')

  except Exception as e:
    return (False, f'Unexpected error: {e}')
