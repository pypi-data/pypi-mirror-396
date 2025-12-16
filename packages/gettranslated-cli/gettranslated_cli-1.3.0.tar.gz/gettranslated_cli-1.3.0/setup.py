"""Setup script for gettranslated-cli package"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="gettranslated-cli",
    version="1.3.0",
    author="GetTranslated",
    author_email="support@gettranslated.ai",
    description="Command-line tool for syncing translations with GetTranslated.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.gettranslated.ai",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Localization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "translate=gettranslated_cli.main:main",
            "gettranslated=gettranslated_cli.main:main",
        ],
    },
    keywords="translation localization i18n l10n cli android ios react-native",
    project_urls={
        "Documentation": "https://www.gettranslated.ai/developers/cli-quickstart/",
    },
)

