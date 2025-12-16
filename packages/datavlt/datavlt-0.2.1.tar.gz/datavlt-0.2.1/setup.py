from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="datavlt",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "mfsapi>=0.1.1"
    ],
    python_requires=">=3.10",
    author="maksalmaz",
    description="A simple JSON-based data storage library with mfsapi integration",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)