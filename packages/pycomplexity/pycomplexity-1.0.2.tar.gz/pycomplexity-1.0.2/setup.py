from setuptools import setup, find_packages

setup(
    name="pycomplexity",
    version="1.0.2",
    author="Oracle",
    author_email="unknownfrench@proton.me",
    description="runtime complexity analyzer for python",
    url="https://github.com/oracle-dsc/pycomplexity",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
)
