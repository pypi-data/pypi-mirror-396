"""
Setup script for FloquetTB package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="floquettb",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for Floquet engineering of tight-binding models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/floquettb",
    packages=find_packages(exclude=["tests", "examples"]),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="floquet, tight-binding, topology, condensed-matter, physics",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/floquettb/issues",
        "Source": "https://github.com/yourusername/floquettb",
        "Documentation": "https://github.com/yourusername/floquettb#readme",
    },
)

