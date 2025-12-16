# This is a mockup library used for OCR of identity documents.

# Passport


A Python library for extracting information from passports using OCR (Tesseract). It supports parsing MRZ (Machine Readable Zone) and extracting additional fields like "Place of Issue" and "Date of Issue" from the visual zone.

## Features

*   **Robust MRZ Parsing**: Handles common OCR errors, corrects line lengths, and supports various MRZ formats (TD1, TD2, TD3).
*   **Full Text Extraction**: Extracts non-MRZ fields like `Place of Issue` and `Date of Issue`.
*   **Data Formatting**:
    *   Dates are standardized to `dd-MM-YYYY`.
    *   Country codes are converted to full country names (e.g., `VNM` -> `Vietnam`).
    *   Names are converted to Title Case (e.g., `NGUYEN VAN A` -> `Nguyen Van A`).
*   **Input Flexibility**: Accepts image file paths or Base64 encoded strings.
*   **Fallback Logic**: If `Date of Issue` is missing, it can infer it from `Expiry Date` (Expiry - 10 years).

## Prerequisites

You need to have **Tesseract OCR** installed on your system.

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev
```

### Linux (Rocky/RHEL/CentOS)
```bash
sudo dnf install epel-release
sudo dnf install tesseract
```

> [!NOTE]
> If you encounter version conflicts with language packs, installing just `tesseract` is often sufficient as it usually includes English data. If you need other languages, ensure the version matches the installed tesseract version.

### macOS
```bash
brew install tesseract
```

### Windows
Download and install the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

## Installation

1.  Clone this repository.
2.  Install Python dependencies:

```bash
pip install m-ocr-mockup
```

## Usage

### Basic Usage (File Path)

```python
from identity_ocr import read_passport

# Path to your passport image
image_path = "path/to/passport.jpg"

result = read_passport(image_path)

print(result)
```

### Advanced Usage (Base64)

You can pass a Base64 string directly (with or without the `data:image/...;base64,` header).

```python
from identity_ocr import read_passport

# Your base64 string
base64_string = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."

result = read_passport(base64_string)

print(result)
```

## Output Format

The library returns a dictionary with the extracted fields:

```python
{
    'fullname': '',       # Combined Surname + Name (Title Case)
    'surname': '',
    'name': '',
    'sex': 'M',                      # M or F
    'birth_date': '',      # dd-MM-YYYY
    'expiry_date': '',     # dd-MM-YYYY
    'date_of_issue': '',   # dd-MM-YYYY (Extracted or Calculated)
    'place_of_issue': '', # Extracted from visual zone
    'document_number': '',
    'nationality': '',        # Full country name
    'country': '',            # Issuing country
    'type': '',                   # Passport type (TD3 is standard)
    'valid': True,                   # True if MRZ checksums are valid
    'raw_mrz': [...]                 # List of MRZ lines (for debugging)
}
```

## Notes

*   **Image Quality**: High-resolution, glare-free images work best.
*   **Language Support**: The library uses Tesseract's English model (`eng`) by default. It works well for most passports (including Vietnamese) as they are bilingual.
