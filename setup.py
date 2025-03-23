from setuptools import setup, find_packages

setup(
    name="pyzettelkasten",
    version="0.3.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "pyzettelkasten=pyzettelkasten.cli:cli",
        ],
    },
    author="David Bader",
    author_email="davbader@outlook.de",
    description="A CLI tool for managing Zettelkasten notes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iamdavidbader/pyzettelkasten",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)