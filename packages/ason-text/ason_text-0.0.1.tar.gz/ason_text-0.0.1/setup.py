from setuptools import setup, find_packages

setup(
    name="ason-text",
    version="0.0.1",
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[],
    author="Mahir",
    description="Fast and clean alternative to JSON called ASON",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/ason-mahir",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
