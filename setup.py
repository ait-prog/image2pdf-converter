from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="image2pdf-converter",
    version="2.0.0",
    author="legolas2k",
    author_email="qwereqweqw17@gmail.com",
    description="Advanced Image to PDF Converter with GUI and CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/legolas2k/image2pdf-converter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "Pillow>=10.0.0",
        "PyQt6>=6.0.0",
        "tqdm>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "image2pdf=cli.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    package_data={
        "": ["*.ui", "*.qrc", "icons/*"],
    },
)