from setuptools import setup, find_packages

setup(
    name="devtools-base64",
    version="1.0.0",
    description="Base64 encoder/decoder with UTF-8 support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DevTools.at",
    author_email="hello@devtools.at",
    url="https://devtools.at/tools/base64",
    project_urls={
        "Homepage": "https://devtools.at/tools/base64",
        "Repository": "https://github.com/nicokant/base64",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
