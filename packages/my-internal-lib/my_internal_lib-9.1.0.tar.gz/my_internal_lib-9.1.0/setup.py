from setuptools import setup, find_packages

setup(
    name="my-internal-lib",          # MUST be unique on PyPI
    version="9.1.0",
    packages=find_packages(),
    description="My awesome package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my-awesome-package",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
