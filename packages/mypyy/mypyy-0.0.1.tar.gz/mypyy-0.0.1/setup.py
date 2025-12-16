from setuptools import setup, find_packages

setup(
    name="mypyy",
    version="0.0.1",
    author="Ymepy",
    author_email="yome@example.com",
    description="A Python package containing 13 basic Python practicals",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mypyy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
