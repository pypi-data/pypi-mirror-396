from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def parse_requirements(filename):
    """Parse requirements.txt and return a list of requirements."""
    requirements = []
    package_name = "multimodal-parsers"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines, comments, and editable installs
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                # Handle -r includes (optional, for nested requirements)
                if line.startswith("-r"):
                    continue
                # Remove inline comments
                if "#" in line:
                    line = line.split("#")[0].strip()
                # Skip the package itself to avoid circular dependency
                if line and not line.startswith(package_name):
                    requirements.append(line)
    return requirements


# Read requirements from requirements.txt
install_requires = parse_requirements("requirements.txt")

setup(
    name="multimodal-parsers",
    version="0.1.4",
    author="Uyen Hoang",
    author_email="thho00003@stud.uni-saarland.de",
    description="PDF processing pipeline: remove headers/footers, convert to markdown, and generate image captions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thuuyen98/PIER-QA",
    packages=find_packages(exclude=["Preprocessing", "marker", "Database", "Evaluation", "Raptor", "venv", "*.tests", "*.tests.*", "tests.*", "tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "multimodal-parsers=file_parser.cli:main",
        ],
    },
    include_package_data=True,
)
