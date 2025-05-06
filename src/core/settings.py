from PyQt6.QtCore import QSettings

class AppSettings:
    """Класс для управления настройками приложения"""

    def __init__(self):
        self.settings = QSettings("ImageToPDF", "ImageToPDFConverter")

    @property
    def last_directory(self) -> str:
        return self.settings.value("last_directory", "", str)

    @last_directory.setter
    def last_directory(self, value: str):
        self.settings.setValue("last_directory", value)

    @property
    def window_geometry(self) -> bytes:
        return self.settings.value("window_geometry")

    @window_geometry.setter
    def window_geometry(self, value: bytes):
        self.settings.setValue("window_geometry", value)

    @property
    def pdf_quality(self) -> int:
        return self.settings.value("pdf_quality", 90, int)

    @pdf_quality.setter
    def pdf_quality(self, value: int):
        self.settings.setValue("pdf_quality", value)

    @property
    def pdf_dpi(self) -> int:
        return self.settings.value("pdf_dpi", 300, int)

    @pdf_dpi.setter
    def pdf_dpi(self, value: int):
        self.settings.setValue("pdf_dpi", value)