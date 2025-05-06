from PIL import Image
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ImageConverter:
    """Основной класс для конвертации изображений в PDF"""

    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"]

    def __init__(self, quality: int = 90, dpi: int = 300):
        self.quality = quality
        self.output_dpi = dpi
        self._validate_settings()

    def _validate_settings(self):
        """Проверка корректности настроек"""
        if not 1 <= self.quality <= 100:
            raise ValueError("Quality must be between 1 and 100")
        if self.output_dpi <= 0:
            raise ValueError("DPI must be positive")

    def get_image_files(self, path: str) -> List[str]:
        """Получить все поддерживаемые изображения из директории"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        return [
            str(f) for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

    def validate_image(self, file_path: str) -> bool:
        """Проверить, что файл является валидным изображением"""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image file {file_path}: {str(e)}")
            return False

    def convert_to_pdf(
            self,
            image_paths: List[str],
            output_path: str,
            quality: Optional[int] = None,
            dpi: Optional[int] = None
    ) -> str:
        """Конвертировать список изображений в PDF"""
        if not image_paths:
            raise ValueError("No images provided for conversion")

        quality = quality or self.quality
        dpi = dpi or self.output_dpi

        images = []
        for file_path in image_paths:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported file format: {file_path}")

            try:
                img = Image.open(file_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                raise RuntimeError(f"Error processing {file_path}: {str(e)}")

        if not images:
            raise RuntimeError("No valid images available for PDF creation")

        output_path = Path(output_path)
        if output_path.suffix.lower() != '.pdf':
            output_path = output_path.with_suffix('.pdf')

        try:
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                quality=quality,
                dpi= (dpi,dpi))
            return str(output_path)
        except Exception as e:
            raise RuntimeError(f"PDF creation failed: {str(e)}")