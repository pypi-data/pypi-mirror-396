from setuptools import setup

def get_long_description(path):
    """Opens and fetches text of long descrition file."""
    with open(path, 'r') as f:
        text = f.read()
    return text

setup(
    name='csemod',
    version='0.0.4',
    description="Personal Project - Education Purpose Only",
    license="CC0-1.0",
    long_description=get_long_description('README.md'),
    long_description_content_type="text/markdown",
    author='BonzoDon',
    classifiers=[
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords=[],
    install_requires=[
        'pyperclip',
    ],
    packages=["csemod"],
    python_requires='>=3.6',
)
