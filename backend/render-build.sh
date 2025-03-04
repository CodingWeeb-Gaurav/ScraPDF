#!/usr/bin/env bash

# Update and install dependencies
apt-get update
apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng \  # Add required languages
    poppler-utils  # Required for pdf2image

pip install -r requirements.txt
