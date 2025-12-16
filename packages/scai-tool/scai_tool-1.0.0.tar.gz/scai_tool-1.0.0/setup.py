from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
# We wrap this in a try-except block so it doesn't fail if README is missing during local dev
try:
    README = (HERE / "README.md").read_text(encoding='utf-8')
except FileNotFoundError:
    README = "A tool to generate directory structures from AI text trees."

setup(
    name="scai-tool",  # The new package name
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            # Now the command in the terminal is 'scai'
            'scai=scaffolder.cli:main', 
        ],
    },
    install_requires=[],
    author="kaus-04",
    author_email="kaus77135@gmail.com",
    description="A developer tool that turns AI-generated directory tree text into actual files and folders.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kaus-04/scai", 
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)