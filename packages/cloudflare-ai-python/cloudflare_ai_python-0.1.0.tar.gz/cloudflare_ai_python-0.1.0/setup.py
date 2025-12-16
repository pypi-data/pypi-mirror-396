from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cloudflare-ai-python",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python client for Cloudflare Workers AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/him6794/cloudflare-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
    ],
)