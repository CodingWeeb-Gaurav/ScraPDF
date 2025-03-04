#!/usr/bin/env bash

# Install Tesseract-OCR
curl -fsSL https://raw.githubusercontent.com/tesseract-ocr/tesseract/main/install_scripts/install_latest.sh | bash

# Install dependencies
pip install -r requirements.txt
