from setuptools import setup, find_packages

def readme() -> str:
    with open("README.md", "r", encoding = "utf-8") as f:
        return f.read()

setup(
    name = "golden-utils",
    version = "0.1.2",
    packages = find_packages(where = "src"),
    package_dir = {"": "src"},

    author = "Golden Dev",
    author_email = "miguizin.10@gmail.com",
    description = "Utilities for annoying or slowing details, like capitalizing booleans",
    long_description = readme(),
    long_description_content_type = "text/markdown; charset=UTF-8",
    url = "https://github.com/Goldencubist/golden-utils",
    license = "MIT",

    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires = ">=3.8"
)