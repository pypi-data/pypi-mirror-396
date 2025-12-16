"""
Setup file for Flask OpenAPI Documentation Package.

This file allows the package to be installed using pip install.
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    find_packages = lambda: ['quas_docs']

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A reusable package for generating comprehensive OpenAPI documentation with Flask-Pydantic-Spec"

setup(
    name="quas-docs",
    version="0.0.9",
    author="Emmanuel Olowu",
    author_email="zeddyemy@gmail.com",
    description="A reusable package for generating comprehensive OpenAPI documentation with Flask-Pydantic-Spec",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zeddyemy/quas-docs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.12",
    install_requires=[
        "flask>=2.0.0",
        "pydantic>=2.0.0",
        "flask-pydantic-spec>=0.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.900",
        ],
    },
    keywords="flask openapi swagger documentation api pydantic",
    project_urls={
        "Bug Reports": "https://github.com/zeddyemy/quas-docs/issues",
        "Source": "https://github.com/zeddyemy/quas-docs",
        "Documentation": "https://github.com/zeddyemy/quas-docs#readme",
    },
)
