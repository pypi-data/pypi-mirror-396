from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="datatrust",
    version="0.1.0",
    author="Aditya kumar goswami",
    author_email="goswamiaditya147@gmail.com",
    description="Detect untrustworthy, fabricated, or suspicious data in datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aditya10m/datatrust",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn"
    ],
    python_requires=">=3.13",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    entry_points={
        "console_scripts": [
            "datatrust=datatrust.cli:main"
        ]
    },
)
