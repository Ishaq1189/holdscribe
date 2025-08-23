#!/usr/bin/env python3
"""Setup script for HoldScribe"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="holdscribe",
    version="1.3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Hold a key to record, release to transcribe and paste at cursor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ishaq1189/holdscribe",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai-whisper>=20240930",
        "pyaudio>=0.2.11",
        "pynput>=1.7.6",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "holdscribe=holdscribe:main",
        ],
    },
    include_package_data=True,
)