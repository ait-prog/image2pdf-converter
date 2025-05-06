import argparse
from pathlib import Path
import sys
import logging
from datetime import datetime
from typing import List
from src.core.converter import ImageConverter


def setup_logging() -> logging.Logger:
    """Настройка системы логирования"""
    log_filename = f"image_to_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Разбор аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Image to PDF Converter - Command Line Interface',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'input',
        nargs='+',
        help='Input image files or directories'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=90,
        choices=range(1, 101),
        metavar="1-100",
        help='Output quality (1-100)'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='Output DPI resolution'
    )
    return parser.parse_args()


def collect_image_paths(input_paths: List[str], converter: ImageConverter) -> List[str]:
    """Собрать пути к изображениям из входных аргументов"""
    image_paths = []
    for path in input_paths:
        path = Path(path)
        if not path.exists():
            print(f"Warning: Path does not exist - {path}", file=sys.stderr)
            continue

        if path.is_file():
            if path.suffix.lower() in converter.SUPPORTED_FORMATS:
                image_paths.append(str(path))
        elif path.is_dir():
            try:
                dir_files = converter.get_image_files(str(path))
                image_paths.extend(dir_files)
            except Exception as e:
                print(f"Error processing directory {path}: {e}", file=sys.stderr)
    return image_paths


def main():
    """Точка входа CLI"""
    logger = setup_logging()
    try:
        args = parse_args()
        converter = ImageConverter(quality=args.quality, dpi=args.dpi)

        logger.info("Starting conversion with settings: %s", vars(args))
        image_paths = collect_image_paths(args.input, converter)

        if not image_paths:
            logger.error("No valid images found")
            print("Error: No valid image files found", file=sys.stderr)
            sys.exit(1)

        logger.info("Found %d images for conversion", len(image_paths))
        output_path = converter.convert_to_pdf(image_paths, args.output)

        logger.info("PDF successfully created: %s", output_path)
        print(f"Successfully created PDF: {output_path}")

    except Exception as e:
        logger.exception("Conversion failed")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()