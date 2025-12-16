from setuptools import setup, find_packages, Extension
# from Cython.Build import cythonize
import os
import shutil

# Fix for missing gcc-11: Force use of system gcc if gcc-11 is not found
if os.environ.get("CC") is None:
    if shutil.which("gcc-11") is None and shutil.which("gcc") is not None:
        os.environ["CC"] = "gcc"

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define extensions
# We want to compile all .py files in src/identity_ocr as separate extensions
# extensions = []
# package_dir = os.path.join("src", "identity_ocr")

# Ensure the directory exists before trying to list its contents
# if os.path.isdir(package_dir):
#     for filename in os.listdir(package_dir):
#         if filename.endswith(".py") and filename != "__init__.py":
#             module_name = f"identity_ocr.{filename[:-3]}"
#             file_path = os.path.join(package_dir, filename)
#             extensions.append(Extension(module_name, [file_path]))

setup(
    name="identity-ocr",
    version="0.1.14",
    description="A robust Python library for extracting information from passports using OCR (Tesseract) and MRZ parsing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    python_requires=">=3.7",
    install_requires=[
        "pytesseract",
        "opencv-python-headless",
        "mrz",
        "numpy"
    ],
)
