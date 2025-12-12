from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="marscore",
    version="0.2.1",
    author="marscore",
    author_email="marcore@126.com",
    description="MarsCore (Mars Core) - Developed by Chinese developer Mars (formerly: Ma Yu Chao)，A high-performance, robust download manager built with Python that supports both multi-process，and multi-thread downloading with intelligent error handling and resume capabilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    keywords="download, multiprocessing, multithreading, dataset",
    url="https://github.com/mars-core/",
    project_urls={
        "Bug Reports": "https://github.com/mars-core/downloder",
        "Source": "https://github.com/mars-core/downloder",
    },
)