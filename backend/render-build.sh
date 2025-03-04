#!/usr/bin/env bash

# Ensure the system package lists are updated
apt-get update

# Install Tesseract OCR
apt-get install -y tesseract-ocr

# Install all Python dependencies
pip install -r requirements.txt
