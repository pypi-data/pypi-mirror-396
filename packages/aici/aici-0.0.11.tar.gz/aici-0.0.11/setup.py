# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup, find_packages


def read_version():
    import os

    version = {}
    filename = os.path.join(
        os.path.join(os.path.dirname(__file__), "aici"), "version.py"
    )
    with open(filename, "r", encoding="utf-8") as f:
        exec(f.read(), version)
    return version["__version__"]


setup(
    name="aici",
    version=read_version(),
    packages=find_packages(exclude=['tests', 'tests.*', '*.tests', '*.tests.*']),
    package_data={
        'aici': ['*.py', '*.md'],
    },
    exclude_package_data={
        'aici': ['mock_api.py', 'run_e2e_tests.sh', 'run_e2e_tests_mocked.sh'],
    },
    description="A command line interface for ChatGPT",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tkykszk/aici/",
    license="MIT",
    include_package_data=True,
    install_requires=[
        "openai>=1.39.0",  # for compatibility with Py3.7
        "pytest",
        "pyperclip",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "aici=aici.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Python version
)
