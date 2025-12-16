"""
setup.py - SerpentUI Package Configuration v2.0
Flask + WebView Integration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="serpentui",
    version="2.0.0",
    author="SerpentUI Team",
    author_email="adriandevelopment.dev@gmail.com",
    description="Modern Python Desktop Apps with React, NextUI, Flask & WebView - Just Click Run!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adrianez28/serpentui",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.0.0",
        "pywebview>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "mypy>=0.950",
            "flake8>=4.0",
        ],
        "full": [
            "Flask>=2.0.0",
            "pywebview>=4.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            # "serpentui=serpentui.cli:main", # CLI not implemented yet
        ],
    },
    keywords="ui framework react nextui python web gui desktop flask webview",
    project_urls={
        "Documentation": "https://github.com/adrianez28/readme.md",
        "Source": "https://github.com/adrianez28/serpentui",
    },
)
