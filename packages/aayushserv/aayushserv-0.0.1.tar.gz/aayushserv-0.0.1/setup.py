from setuptools import setup, find_packages

setup(
    name="aayushserv",       # must be unique on PyPI
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],     # no extra dependencies
    python_requires='>=3.8',
    description="Super simple local server for HTML login forms",
    author="Aayush",
    url="https://github.com/Aayushbohora",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
