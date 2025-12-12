from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

docs_require = [
    "griffe==0.42.0",
    "markdown==3.5.2",
    "markdown-include==0.8.1",
    "mkdocs-git-revision-date-localized-plugin==1.2.4",
    "mkdocs-include-markdown-plugin==6.0.4",
    "mkdocs-material==9.5.13",
    "mkdocstrings-python==1.9.0",
    "mkdocs-autorefs==1.3.1",
]

tests_require = [
    "coverage==7.4.4",
    "coverage-badge==1.1.0",
    "flake8==7.0.0",
    "mypy==1.9.0",
    "pylint==3.1.0",
    "pytest==8.1.1",
    "pytest-cov==4.1.0",
    "pytest-subtests==0.12.1",
]

build_require = [
    "setuptools==69.2.0",
    "wheel==0.45.1",
    "twine==6.0.1",
]

all_requirements = required + docs_require + tests_require + build_require

setup(
    name="fiqus",
    version="2025.12.0",
    author="STEAM Team",
    author_email="steam-team@cern.ch",
    description="Source code for STEAM FiQuS tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/steam/fiqus",
    keywords=["STEAM", "FiQuS", "CERN"],
    install_requires=required,
    extras_require={
        "all": all_requirements,
        "docs": docs_require,
        "tests": tests_require,
        "build": build_require,
    },
    python_requires=">=3.11",
    packages=find_packages(),
    package_data={
        "fiqus": [
            "**/*.pro",
        ]
    },
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3.11"],
)
