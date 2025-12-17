from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pdftradoc",
    version="1.0.0",
    author="PdfTradoc",
    description="A Python library for translating PDF documents while preserving the original layout",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyMuPDF>=1.23.0",
        "deep-translator>=1.11.0",
        "Pillow>=10.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    keywords="pdf translation translate document overlay layout preserve",
)
