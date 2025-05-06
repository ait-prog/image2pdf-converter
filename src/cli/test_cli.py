import pytest
from unittest.mock import patch, MagicMock
from src.cli.cli import collect_image_paths, main
import sys


@pytest.fixture
def mock_converter():
    converter = MagicMock()
    converter.SUPPORTED_FORMATS = [".jpg", ".png"]
    converter.get_image_files.return_value = ["/path/to/image1.jpg", "/path/to/image2.png"]
    return converter


def test_collect_image_paths_with_files(mock_converter):
    input_paths = ["test1.jpg", "test2.png"]
    result = collect_image_paths(input_paths, mock_converter)
    assert len(result) == 2
    assert "test1.jpg" in result
    assert "test2.png" in result


def test_collect_image_paths_with_unsupported_files(mock_converter, capsys):
    input_paths = ["test1.jpg", "test.txt"]
    result = collect_image_paths(input_paths, mock_converter)
    assert len(result) == 1
    assert "Warning: Unsupported file format" in capsys.readouterr().err


def test_collect_image_paths_with_directory(mock_converter):
    input_paths = ["test_dir"]
    result = collect_image_paths(input_paths, mock_converter)
    mock_converter.get_image_files.assert_called_once_with("test_dir")
    assert len(result) == 2


@patch("cli.ImageConverter")
@patch("cli.parse_args")
def test_main_success(mock_parse_args, mock_converter_class, tmp_path):
    output_pdf = tmp_path / "output.pdf"
    mock_args = MagicMock()
    mock_args.input = ["test.jpg"]
    mock_args.output = str(output_pdf)
    mock_args.quality = 90
    mock_args.dpi = 300
    mock_parse_args.return_value = mock_args

    mock_converter = MagicMock()
    mock_converter_class.return_value = mock_converter
    mock_converter.convert_to_pdf.return_value = str(output_pdf)

    with patch.object(sys, 'argv', ['cli.py', 'test.jpg', '-o', str(output_pdf)]):
        main()

    assert output_pdf.exists()