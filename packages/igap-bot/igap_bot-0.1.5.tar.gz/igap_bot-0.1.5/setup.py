from setuptools import setup, find_packages

setup(
    name="igap-bot",
    version="0.1.5",
    description="Unofficial iGap Bot API client for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ehsan",
    author_email="Botkaplus@gmail.com",
    url="https://github.com/sinyor-ehsan/igap-bot",
    packages=find_packages(),
    install_requires=[
        "protobuf>=3.19.0,<4.0.0",
        "aiohttp>=3.8.0",
        "Pillow>=9.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)