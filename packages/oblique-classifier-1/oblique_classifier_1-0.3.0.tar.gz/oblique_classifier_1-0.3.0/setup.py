"""
Setup script for OC1 package.

OC1: Oblique Classifier 1 - A Python implementation of the OC1 oblique
decision tree algorithm (Murthy et al., AAAI-1992).
"""

from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="oblique-classifier-1",
    version="0.3.0",
    description="OC1 Oblique Decision Tree - Implementation of Murthy et al. (AAAI-1992)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RJILI Houssam, Fatima-Ezzahrae AKEBLI, Yasser",
    author_email="houssam.rjili@example.com",
    url="https://github.com/HxRJILI/Oblique-Classifier-1",
    project_urls={
        "Bug Tracker": "https://github.com/HxRJILI/Oblique-Classifier-1/issues",
        "Source Code": "https://github.com/HxRJILI/Oblique-Classifier-1",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=[
        "machine-learning",
        "decision-tree",
        "oblique-tree",
        "classification",
        "oc1",
        "murthy",
    ],
    include_package_data=True,
    zip_safe=False,
)
