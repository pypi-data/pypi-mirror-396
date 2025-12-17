from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from package
with open("src/storage_viewer/__init__.py", "r", encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="storage-viewer-cli",  # This should match the wheel file name
    version=version,
    author="Lingaraj Sa",
    author_email="infofusiontechlab@gmail.com",
    description="Advanced directory tree visualizer with filtering options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/infofusiontechlab/storage-viewer",
    project_urls={
        "Bug Tracker": "https://github.com/infofusiontechlab/storage-viewer/issues",
        "Source Code": "https://github.com/infofusiontechlab/storage-viewer",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "stree=storage_viewer.storage_viewer:main",
            "storage-viewer=storage_viewer.storage_viewer:main",
        ],
    },
)
