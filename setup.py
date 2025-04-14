from setuptools import setup, find_packages
import os

# Read the contents of your README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="metasearch",
    version="0.4.2",
    description="A file management and metadata search library.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Change to "text/x-rst" if you use reStructuredText
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/metasearch",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.0.0",
        "exifread>=2.3.2",
        "mutagen>=1.45.1",
        "PyMuPDF>=1.18.19",
        "python-docx>=0.8.11",
        "openpyxl>=3.0.7",
        "python-pptx>=0.6.21",
        "watchdog>=2.1.6",
        "chardet>=4.0.0",
        "ffmpeg-python>=0.2.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
