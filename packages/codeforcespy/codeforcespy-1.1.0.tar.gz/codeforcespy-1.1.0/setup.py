from setuptools import find_packages
from setuptools import setup

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

_ = setup(
    name="codeforcespy",
    version="1.1.0",
    author="Xsyncio",
    description=(
        "A high-performance and type-safe Python library for seamless interaction "
        "with the Codeforces API. Supports both asynchronous and synchronous client "
        "handlers, enabling developers to choose the best approach for their needs."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xsyncio/codeforcespy",
    packages=find_packages(include=["codeforcespy", "codeforcespy.*"]),
    include_package_data=True,
    install_requires=[
        "httpx>=0.23.0",
        "msgspec>=0.18.0",
    ],
    extras_require={
        "dev": [
            "ruff",
            "pytest",
            "mypy",
            "basedpyright",
            "respx",
            "build",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    keywords=[
        "python",
        "codeforces",
        "api",
        "wrapper",
        "async",
        "sync",
        "type-safe",
        "competitive-programming",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/xsyncio/codeforcespy/issues",
        "Documentation": "https://github.com/xsyncio/codeforcespy",
        "Source": "https://github.com/xsyncio/codeforcespy",
    },
)
