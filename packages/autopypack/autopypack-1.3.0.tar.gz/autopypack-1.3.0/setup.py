from setuptools import setup, find_packages

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autopypack",
    version="1.3.0",
    description="Automatically installs missing Python libraries when running your code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harsh Jaiswal",
    author_email="harshrajjaiswal16012003@gmail.com",
    url="https://github.com/harshRaj1601/AutoPyPack",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "AutoPyPack.autopypack": ["mappings.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "ipython>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "autopypack=AutoPyPack.autopypack.cli:main",
        ],
    },
)
