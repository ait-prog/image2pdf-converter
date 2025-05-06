import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QInputDialog, QLineEdit, QStyleFactory, QListWidgetItem,
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
)
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter, QFont
from PyQt6.QtCore import Qt, QSize, QMimeData, QUrl
from PIL import Image
import logging
from datetime import datetime
from PyQt6.QtWidgets import QListWidget
import asyncio


# Настройка логирования
def setup_logging():
    log_dir = Path("../../../../logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"converter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class ImageConverter:
    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"]

    def __init__(self):
        self.quality = 90
        self.output_dpi = 300


    def validate_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image file {file_path}: {str(e)}")
            return False


class ImageToPDFApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = ImageConverter()
        self.current_preview_index = -1
        self.init_ui()
        self.setup_connections()
        self.setAcceptDrops(True)

    def init_ui(self):
        self.setWindowTitle("Image to PDF Converter v2.0")
        self.setMinimumSize(800, 600)

        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель - список файлов
        left_panel = QVBoxLayout()

        # Список файлов
        self.list_widget = FileListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        left_panel.addWidget(QLabel("Selected Images:"))
        left_panel.addWidget(self.list_widget)

        # Кнопки управления списком
        btn_layout = QHBoxLayout()

        self.btn_add_files = QPushButton("Add Files")
        self.btn_add_files.setIcon(QIcon.fromTheme("document-open"))
        self.btn_add_folder = QPushButton("Add Folder")
        self.btn_add_folder.setIcon(QIcon.fromTheme("folder-open"))
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.setIcon(QIcon.fromTheme("edit-delete"))

        btn_layout.addWidget(self.btn_add_files)
        btn_layout.addWidget(self.btn_add_folder)
        btn_layout.addWidget(self.btn_remove)
        left_panel.addLayout(btn_layout)

        # Правая панель - предпросмотр и управление
        right_panel = QVBoxLayout()

        # Область предпросмотра
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        right_panel.addWidget(QLabel("Preview:"))
        right_panel.addWidget(self.preview_label, 1)

        # Кнопки управления
        move_btn_layout = QHBoxLayout()
        self.btn_move_up = QPushButton("Move Up")
        self.btn_move_up.setIcon(QIcon.fromTheme("go-up"))
        self.btn_move_down = QPushButton("Move Down")
        self.btn_move_down.setIcon(QIcon.fromTheme("go-down"))

        move_btn_layout.addWidget(self.btn_move_up)
        move_btn_layout.addWidget(self.btn_move_down)
        right_panel.addLayout(move_btn_layout)

        # Кнопки конвертации
        self.btn_convert = QPushButton("Convert to PDF")
        self.btn_convert.setStyleSheet(
            "background-color: #1976D2; color: white; font-weight: bold; padding: 8px;"
        )
        self.btn_clear = QPushButton("Clear All")

        right_panel.addWidget(self.btn_convert)
        right_panel.addWidget(self.btn_clear)

        # Добавляем панели в основной layout
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 2)
        # Статус бар
        self.statusBar().showMessage("Ready")

    # self.btn_add_folder.clicked.connect(self.add_folder)
    # self.btn_remove.clicked.connect(self.remove_selected)
    # self.btn_move_up.clicked.connect(self.move_up)
    # self.btn_move_down.clicked.connect(self.move_down)
    # self.btn_convert.clicked.connect(self.convert_to_pdf)
    # self.btn_clear.clicked.connect(self.clear_list)
    # self.list_widget.currentRowChanged.connect(self.update_preview)

    def setup_connections(self):
        self.btn_add_files.clicked.connect(self.add_files)
        self.btn_add_folder.clicked.connect(self.add_folder)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_move_up.clicked.connect(self.move_up)
        self.btn_move_down.clicked.connect(self.move_down)
        self.btn_convert.clicked.connect(self.convert_to_pdf)
        self.btn_clear.clicked.connect(self.clear_list)
        self.list_widget.currentRowChanged.connect(self.update_preview)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()


    def dropEvent(self, event):
        urls = event.mimeData().urls()
        valid_files = []

        for url in urls:
            file_path = url.toLocalFile()
            path = Path(file_path)

            if path.is_file() and path.suffix.lower() in self.converter.SUPPORTED_FORMATS:
                if self.converter.validate_image(file_path):
                    valid_files.append(file_path)
            elif path.is_dir():
                try:
                    for f in path.iterdir():
                        if f.is_file() and f.suffix.lower() in self.converter.SUPPORTED_FORMATS:
                            if self.converter.validate_image(str(f)):
                                valid_files.append(str(f))
                except Exception as e:
                    logger.error(f"Error processing directory {file_path}: {str(e)}")

        if valid_files:
            self.add_files_to_list(valid_files)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tiff)"
        )
        if files:
            valid_files = [f for f in files if self.converter.validate_image(f)]
            if valid_files:
                self.add_files_to_list(valid_files)
            else:
                QMessageBox.warning(self, "No Valid Images", "No valid image files were selected.")

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Images")
        if folder:
            valid_files = []
            for f in Path(folder).iterdir():
                if f.is_file() and f.suffix.lower() in self.converter.SUPPORTED_FORMATS:
                    if self.converter.validate_image(str(f)):
                        valid_files.append(str(f))

            if valid_files:
                self.add_files_to_list(valid_files)
            else:
                QMessageBox.warning(self, "No Valid Images", "No valid image files found in the selected folder.")

    def add_files_to_list(self, files):
        existing_files = {self.list_widget.item(i).text() for i in range(self.list_widget.count())}
        new_files = [f for f in files if f not in existing_files]

        if not new_files:
            QMessageBox.information(self, "Info", "All selected files are already in the list")
            return

        for file_path in new_files:
            item = QListWidgetItem()
            item.setText(file_path)
            item.setIcon(self.create_file_icon(file_path))
            self.list_widget.addItem(item)

        self.statusBar().showMessage(f"Added {len(new_files)} images")

    def create_file_icon(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return QIcon.fromTheme("image-x-generic")

        thumb_size = QSize(48, 48)
        scaled_pixmap = pixmap.scaled(
            thumb_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        result_pixmap = QPixmap(thumb_size)
        result_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result_pixmap)
        x = (thumb_size.width() - scaled_pixmap.width()) // 2
        y = (thumb_size.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()

        return QIcon(result_pixmap)

    def update_preview(self, index=None):
        if index is None:
            index = self.list_widget.currentRow()

        if index < 0 or index >= self.list_widget.count():
            self.preview_label.clear()
            self.preview_label.setText("No image selected")
            return

        self.current_preview_index = index
        file_path = self.list_widget.item(index).text()

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.preview_label.setText("Cannot display preview")
            return

        preview_size = self.preview_label.size()
        scaled_pixmap = pixmap.scaled(
            preview_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        self.update_preview()
        super().resizeEvent(event)

    def remove_selected(self):
        selected = self.list_widget.selectedItems()
        if not selected:
            return

        if len(selected) == 1:
            message = f"Remove '{Path(selected[0].text()).name}'?"
        else:
            message = f"Remove {len(selected)} selected items?"

        reply = QMessageBox.question(
            self,
            "Remove Items",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected:
                self.list_widget.takeItem(self.list_widget.row(item))

    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)

    def clear_list(self):
        if self.list_widget.count() == 0:
            return

        reply = QMessageBox.question(
            self,
            "Clear All",
            "Clear the entire list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.list_widget.clear()

    def convert_to_pdf(self):
        if self.list_widget.count() == 0:
            QMessageBox.information(self, "Empty List", "Please add images first")
            return

        # Получаем имя файла
        pdf_name, ok = QInputDialog.getText(
            self,
            "PDF Name",
            "Enter PDF filename:",
            QLineEdit.EchoMode.Normal,
            "output"
        )

        if not ok or not pdf_name.strip():
            return

        # Выбираем папку для сохранения
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not directory:
            return

        # Получаем список файлов
        image_paths = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        output_path = str(Path(directory) / f"{pdf_name.strip()}.pdf")

        # Конвертируем
        try:
            images = []
            for file_path in image_paths:
                try:
                    img = Image.open(file_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    raise

            if not images:
                raise ValueError("No valid images available for PDF creation")

            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                quality=self.converter.quality,
                dpi=(self.converter.output_dpi, self.converter.output_dpi)
            )

            QMessageBox.information(
                self,
                "Success",
                f"PDF created successfully:\n{output_path}"
            )
            logger.info(f"PDF successfully created: {output_path}")

        except Exception as e:
            logger.error(f"PDF creation failed: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create PDF:\n{str(e)}"
            )


class FileListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.parent().dropEvent(event)
        else:
            super().dropEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    # Установка стиля для сине-белой темы
    app.setStyleSheet("""
        QMainWindow {
            background-color: #FFFFFF;
        }
        QListWidget {
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
        }
        QLabel {
            color: #212121;
        }
        QPushButton {
            background-color: #1976D2;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2196F3;
        }
    """)

    window = ImageToPDFApp()
    window.show()
    sys.exit(app.exec())