<div align="center">
<a href="https://github.com/oclero/pdfwm">
	<img style="margin-bottom: 2em; width: 640px" src="https://raw.githubusercontent.com/oclero/pdfwm/master/thumbnail.png">
</a>
</div>

# PDF Watermark (pdfwm)

A Python **library** and **command-line tool** for adding text watermarks to PDF files. Supports batch processing, custom colors, and recursive directory processing.

## Features

- 🎨 **Text Watermarks**: Generate watermarks from custom text
- 🎯 **Auto-sizing**: Automatically fits watermark text to page dimensions
- 🌈 **Color Customization**: Support for RGB and RGBA hex color codes
- 📦 **Batch Processing**: Process multiple files with glob patterns
- 🔄 **Recursive Mode**: Preserve directory structure when processing
- 💾 **Safe Overwrite**: Optional in-place modification with temporary file safety
- 🔧 **Library & CLI**: Use as a Python library or command-line tool
- ✨ **Type Hints**: Full type annotation support

|                                             Before Watermark                                              |                                              After Watermark                                              |
| :-------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------: |
| ![Before watermark](https://raw.githubusercontent.com/oclero/pdfwm/master/examples/lorem-ipsum-input.png) | ![After watermark](https://raw.githubusercontent.com/oclero/pdfwm/master/examples/lorem-ipsum-output.png) |

## Installation

### From PyPI

```bash
pip install pdfwm
```

### From Source

```bash
git clone https://github.com/yourusername/pdfwm.git
cd pdfwm
pip install -e .
```

## Command-Line Usage

### Basic Usage

Add watermark to a single file:

```bash
pdfwm -i document.pdf -o watermarked.pdf -t "CONFIDENTIAL"
```

### Batch Processing

Process multiple files with glob patterns:

```bash
# Process all PDFs in current directory
pdfwm -i *.pdf -o output/ -t "DRAFT"

# Process PDFs recursively
pdfwm -i **/*.pdf -o output/ -t "DRAFT" --recursive
```

### Custom Colors

Use hex color codes (RGB or RGBA):

```bash
# Red with 50% opacity
pdfwm -i document.pdf -o output.pdf -t "CONFIDENTIAL" -c "#FF000080"

# Gray (default opacity)
pdfwm -i document.pdf -o output.pdf -t "DRAFT" -c "#808080"
```

### Overwrite Mode

Modify files in-place:

```bash
pdfwm -i document.pdf -t "CONFIDENTIAL" --overwrite
```

### Custom Suffix

When not specifying output path:

```bash
pdfwm -i document.pdf -t "DRAFT" -s "_draft"
# Creates: document_draft.pdf
```

### Full Options

```
pdfwm [options]

Options:
  -i, --input FILE [FILE ...]   Input PDF file(s). Supports wildcards.
  -o, --output PATH             Output file or directory
  -t, --text TEXT               Watermark text (required)
  -c, --color HEX               Watermark color (default: #80808019)
  -s, --suffix SUFFIX           Filename suffix (default: _watermarked)
  -w, --overwrite               Overwrite input files
  -r, --recursive               Preserve directory structure
  --version                     Show version
  -h, --help                    Show help message
```

## Library Usage

### Basic Example

```python
from pdfwm import process_pdf

# Add watermark to a file
success, message = process_pdf(
    input_path="document.pdf",
    output_path="watermarked.pdf",
    watermark_text="CONFIDENTIAL"
)

if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")
```

### Custom Color

```python
from pdfwm import process_pdf

# Apply watermark with custom color
success, message = process_pdf(
    input_path="document.pdf",
    output_path="output.pdf",
    watermark_text="CONFIDENTIAL",
    watermark_color="#FF000080"  # Red with 50% opacity
)
```

## Requirements

- Python 3.8+
- PyPDF2 >= 3.0.0
- reportlab >= 4.0.0

Install dependencies:

```bash
# For users
pip install -r requirements.txt

# For developers
pip install -r requirements-dev.txt
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Author

Olivier Cléro - <oclero@pm.me>
