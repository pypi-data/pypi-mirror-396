"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="svo-client",
    version="2.1.0",
    description="Async client for SVO semantic chunker microservice.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vasiliy Zdanovskiy",
    author_email="vasilyvz@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "chunk_metadata_adapter>=3.2.0",
        "mcp-proxy-adapter>=0.1.0",
    ],
    python_requires=">=3.8",
    url="https://github.com/your_org/svo_client",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "svo-chunker=svo_client.cli:main",
        ]
    },
)
