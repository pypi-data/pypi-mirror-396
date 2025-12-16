# myproject/setup.py

from setuptools import setup, find_packages

setup(
    name="endee-llamaindex",
    version="0.1.3",
    packages=find_packages(include=['endee_llamaindex', 'endee_llamaindex.*']),
    install_requires=[
        # List your dependencies here
        "llama-index>=0.12.34",
        "endee>=0.1.4",
    ],
    author="Endee Labs",
    author_email="vineet@endee.io",
    description="Vector Database for Fast ANN Searches",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://endee.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
