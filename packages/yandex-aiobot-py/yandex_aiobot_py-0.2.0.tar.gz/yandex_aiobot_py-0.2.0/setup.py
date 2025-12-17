from setuptools import setup, find_packages

setup(
    name="yandex-aiobot-py",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
    ],
    author="demkinkv",
    author_email="demkinkv92@yandex.com",
    description="Async bot library for Yandex Messenger",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your/repo",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
