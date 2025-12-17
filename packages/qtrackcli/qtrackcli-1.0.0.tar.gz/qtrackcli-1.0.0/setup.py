# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qtrackcli",
    version="1.0.0",
    author="emily wang",
    author_email="qtrack@126.com",
    description="CLI tool for uploading pytest results to q-track",
    long_description="""
    # qtrackcli
    CLI tool for uploading pytest results to q-track
    """,
    #long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/yourusername/qtrack-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1"
    ],
    entry_points={
        "console_scripts": [
            "qtrackcli=qtrackcli.cli:main",
        ],
    },
)
