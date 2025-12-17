from setuptools import setup, find_packages

setup(
    name="pygrammy",
    version="1.0.0",
    description="PyGrammY — GrammyJS inspired async Telegram Bot framework for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="oscoderuz",
    author_email="oscoderuz@gmail.com",
    url="https://github.com/oscoderuz/pygrammy",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "aiohttp>=3.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="telegram bot async framework grammy pygrammy",
    license="MIT",
)