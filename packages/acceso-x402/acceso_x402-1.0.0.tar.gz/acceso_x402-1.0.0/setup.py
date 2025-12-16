from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="acceso-x402",
    version="1.0.0",
    author="Acceso",
    author_email="dev@acceso.dev",
    description="Python SDK for x402 HTTP payment protocol on Solana",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acceso-dev/acceso-x402-python",
    project_urls={
        "Documentation": "https://docs.acceso.dev",
        "Bug Tracker": "https://github.com/acceso-dev/acceso-x402-python/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
    },
)
