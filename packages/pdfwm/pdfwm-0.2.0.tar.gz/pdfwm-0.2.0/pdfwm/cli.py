"""Command-line interface for PDF watermarking."""

import os
import sys
import argparse
import tempfile
import glob
from typing import List, Tuple

from .core import _parse_hex_color, process_pdf


def main() -> None:
  """Main CLI entry point."""
  # Command-line arguments parser
  parser = argparse.ArgumentParser(
    description='Add a watermark to a PDF file or multiple PDF files.',
    prog='pdfwm')
  parser.add_argument('-i', '--input', nargs='+', required=True,
                      help='Input PDF file path(s). Supports wildcards (e.g., *.pdf) and multiple files.')
  parser.add_argument('-o', '--output', required=False, default=None,
                      help='Output PDF file path (single file) or output directory (batch mode). If not specified and --overwrite not used, adds suffix to input filename.')
  parser.add_argument('-t', '--text', required=True,
                      help='Watermark text to apply.')
  parser.add_argument('-c', '--color', required=False, default=None,
                      help='Watermark color as hex code (RGB or RGBA). Examples: #808080, #FF000033. Default: #80808019.')
  parser.add_argument('-s', '--suffix', required=False, default='_watermarked',
                      help='Suffix to add to input filename when --output is not specified (default: "_watermarked").')
  parser.add_argument('-w', '--overwrite', action='store_true',
                      help='Overwrite the input file instead of creating a new output file.')
  parser.add_argument('-r', '--recursive', action='store_true',
                      help='Enable recursive processing. When used with --output directory, preserves subdirectory structure.')
  parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

  args = parser.parse_args()

  # Validate arguments: cannot specify both output and overwrite
  if args.output and args.overwrite:
    parser.error('Cannot specify both --output and --overwrite')

  # Expand glob patterns and collect all input files
  input_files: List[str] = []
  for pattern in args.input:
    expanded = glob.glob(pattern, recursive=args.recursive)
    if expanded:
      input_files.extend(expanded)
    else:
      # If no glob match, treat as literal filename
      input_files.append(pattern)

  # Remove duplicates while preserving order
  seen = set()
  input_files = [f for f in input_files if not (f in seen or seen.add(f))]

  # Validate: at least one input file
  if len(input_files) == 0:
    parser.error('No input files specified or pattern matched no files')

  watermark_text = args.text
  is_batch_mode = len(input_files) > 1

  # Calculate common base path for recursive mode
  common_base_path = None
  if args.recursive and is_batch_mode and len(input_files) > 0:
    # Find common base directory for all input files
    abs_paths = [os.path.abspath(f) for f in input_files]
    common_base_path = os.path.commonpath(abs_paths)
    # If common path is a file, use its directory
    if os.path.isfile(common_base_path):
      common_base_path = os.path.dirname(common_base_path)

  # Parse color if provided
  watermark_color = None
  if args.color:
    try:
      watermark_color = _parse_hex_color(args.color)
    except ValueError as e:
      print(f'Error: Invalid color format - {e}', file=sys.stderr)
      sys.exit(1)
    except Exception as e:
      print(f'Error: Failed to parse color - {e}', file=sys.stderr)
      sys.exit(1)

  # Batch processing mode
  if is_batch_mode:
    _run_batch_mode(
      input_files, args, watermark_text, watermark_color,
      common_base_path, is_batch_mode
    )
  else:
    # Single file processing mode
    _run_single_mode(input_files[0], args, watermark_text, watermark_color)


def _run_batch_mode(
    input_files: List[str],
    args,
    watermark_text: str,
    watermark_color,
    common_base_path,
    is_batch_mode: bool
) -> None:
  """Run batch processing mode."""
  print(f'Batch mode: Processing {len(input_files)} file(s)...')

  # Create output directory if specified
  output_dir = None
  if args.output:
    output_dir = os.path.abspath(args.output)
    try:
      os.makedirs(output_dir, exist_ok=True)
      print(f'Output directory: {output_dir}')
    except PermissionError:
      print(
        f'Error: Permission denied to create output directory: {output_dir}', file=sys.stderr)
      sys.exit(1)
    except OSError as e:
      print(
        f'Error: Failed to create output directory: {e}', file=sys.stderr)
      sys.exit(1)

  print()

  success_count = 0
  failed_count = 0
  failed_files: List[Tuple[str, str]] = []

  try:
    for idx, input_path in enumerate(input_files, 1):
      input_path = os.path.abspath(input_path)
      print(f'[{idx}/{len(input_files)}] {os.path.basename(input_path)}...')

      # Validate input file
      if not os.path.exists(input_path):
        print(f'  ✗ File not found', file=sys.stderr)
        failed_count += 1
        failed_files.append((input_path, 'File not found'))
        continue

      if not os.path.isfile(input_path):
        print(f'  ✗ Not a file', file=sys.stderr)
        failed_count += 1
        failed_files.append((input_path, 'Not a file'))
        continue

      if not os.access(input_path, os.R_OK):
        print(f'  ✗ File not readable', file=sys.stderr)
        failed_count += 1
        failed_files.append((input_path, 'File not readable'))
        continue

      # Determine output path
      if args.overwrite:
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        output_path = temp_path
      elif output_dir:
        # Use output directory with original filename and suffix
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        output_filename = f"{base_name}{args.suffix}{ext}"

        # If recursive mode, preserve directory structure
        if args.recursive and common_base_path:
          # Get relative path from common base to input file
          rel_path = os.path.relpath(input_path, common_base_path)
          rel_dir = os.path.dirname(rel_path)

          # Apply suffix to filename
          rel_base, rel_ext = os.path.splitext(os.path.basename(rel_path))
          output_filename = f"{rel_base}{args.suffix}{rel_ext}"

          # Construct output path preserving directory structure
          if rel_dir:
            output_subdir = os.path.join(output_dir, rel_dir)
            try:
              os.makedirs(output_subdir, exist_ok=True)
            except (PermissionError, OSError) as e:
              print(
                f'  ✗ Failed to create subdirectory: {e}', file=sys.stderr)
              failed_count += 1
              failed_files.append(
                (input_path, f'Failed to create subdirectory: {e}'))
              continue
            output_path = os.path.join(output_subdir, output_filename)
          else:
            output_path = os.path.join(output_dir, output_filename)
        else:
          # Non-recursive: all files go to output directory root
          output_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_path):
          print(f'  ⚠ Output file exists, will be overwritten')
      else:
        # Use same directory as input with suffix
        base_name, ext = os.path.splitext(input_path)
        output_path = f"{base_name}{args.suffix}{ext}"
        if os.path.exists(output_path):
          print(f'  ⚠ Output file exists, will be overwritten')

      # Process the file
      success, message = process_pdf(
        input_path, output_path, watermark_text, watermark_color, args.overwrite
      )

      if success:
        print(f'  ✓ {message}')
        if not args.overwrite:
          print(f'  → {os.path.basename(output_path)}')
        success_count += 1
      else:
        print(f'  ✗ {message}', file=sys.stderr)
        failed_count += 1
        failed_files.append((input_path, message))
        # Cleanup temp file if overwrite mode failed
        if args.overwrite and os.path.exists(output_path):
          try:
            os.remove(output_path)
          except:
            pass

      print()

  except KeyboardInterrupt:
    print('\n\nOperation cancelled by user', file=sys.stderr)
    sys.exit(130)

  # Print summary
  print('=' * 60)
  print('BATCH PROCESSING SUMMARY')
  print('=' * 60)
  print(f'Total files: {len(input_files)}')
  print(f'Successful:  {success_count}')
  print(f'Failed:      {failed_count}')

  if failed_files:
    print('\nFailed files:')
    for file_path, error in failed_files:
      print(f'  • {os.path.basename(file_path)}: {error}')

  sys.exit(0 if failed_count == 0 else 1)


def _run_single_mode(input_file: str, args, watermark_text: str, watermark_color) -> None:
  """Run single file processing mode."""
  input_path = os.path.abspath(input_file)

  # Validate input file exists
  if not os.path.exists(input_path):
    print(f'Error: Input file not found: {input_path}', file=sys.stderr)
    sys.exit(1)

  # Validate input file is readable
  if not os.path.isfile(input_path):
    print(f'Error: Input path is not a file: {input_path}', file=sys.stderr)
    sys.exit(1)

  if not os.access(input_path, os.R_OK):
    print(
      f'Error: Input file is not readable: {input_path}', file=sys.stderr)
    sys.exit(1)

  # Determine output path
  if args.overwrite:
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd)
    output_path = temp_path
  elif args.output:
    output_path = os.path.abspath(args.output)
    # Ensure output file has .pdf extension
    if not output_path.lower().endswith('.pdf'):
      output_path += '.pdf'
  else:
    base_name, ext = os.path.splitext(input_path)
    output_path = f"{base_name}{args.suffix}{ext}"

  # Check if output file already exists (non-overwrite mode)
  if not args.overwrite and os.path.exists(output_path):
    print(
      f'Warning: Output file already exists and will be overwritten: {output_path}')

  print(f'Input file: {input_path}')

  # Create output directory if it doesn't exist (only when output is specified)
  if args.output:
    output_dir = os.path.dirname(output_path)
    if output_dir:
      try:
        os.makedirs(output_dir, exist_ok=True)
      except PermissionError:
        print(
          f'Error: Permission denied to create output directory: {output_dir}', file=sys.stderr)
        sys.exit(1)
      except OSError as e:
        print(
          f'Error: Failed to create output directory: {e}', file=sys.stderr)
        sys.exit(1)

  # Temporary file path for cleanup in case of error
  temp_output_path = output_path if args.overwrite else None

  try:
    success, message = process_pdf(
      input_path, output_path, watermark_text, watermark_color, args.overwrite
    )

    if success:
      print(message)
      if args.overwrite:
        print(f'File modified in-place: {input_path}')
      else:
        print(f'Output file: {output_path}')
      sys.exit(0)
    else:
      print(f'Error: {message}', file=sys.stderr)
      # Cleanup temporary file if in overwrite mode
      if temp_output_path and os.path.exists(temp_output_path):
        try:
          os.remove(temp_output_path)
        except:
          pass
      sys.exit(1)

  except KeyboardInterrupt:
    print('\nOperation cancelled by user', file=sys.stderr)
    # Cleanup temporary file if in overwrite mode
    if temp_output_path and os.path.exists(temp_output_path):
      try:
        os.remove(temp_output_path)
      except:
        pass
    sys.exit(130)
  except Exception as e:
    print(f'Unexpected error: {e}', file=sys.stderr)
    # Cleanup temporary file if in overwrite mode
    if temp_output_path and os.path.exists(temp_output_path):
      try:
        os.remove(temp_output_path)
      except:
        pass
    sys.exit(1)


if __name__ == '__main__':
  main()
