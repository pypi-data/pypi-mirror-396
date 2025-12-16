"""
Setup script for altsportsleagues package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="altsportsleagues",
    version="1.0.0",
    author="AltSportsLeagues.ai",
    author_email="dev@altsportsleagues.ai",
    description="Python SDK for AltSportsLeagues platform - enabling league owners to get compliant and onboarded with sportsbooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/altsportsleagues/altsportsleagues-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    keywords="sports leagues betting compliance sportsbook api sdk",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    project_urls={
        "Homepage": "https://altsportsleagues.ai",
        "Documentation": "https://docs.altsportsleagues.ai",
        "Repository": "https://github.com/altsportsleagues/altsportsleagues-python",
        "Issues": "https://github.com/altsportsleagues/altsportsleagues-python/issues",
        "Changelog": "https://github.com/altsportsleagues/altsportsleagues-python/blob/main/CHANGELOG.md",
    },
)
