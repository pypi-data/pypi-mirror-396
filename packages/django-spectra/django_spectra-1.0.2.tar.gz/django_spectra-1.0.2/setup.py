"""
Django Spectra - Modern Admin Theme For Django Framework
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-spectra",
    version="1.0.2",
    author="Sundar Adhikari",
    author_email="abcsundaradhikari123@gmail.com",
    description="A modern, customizable, and extensible Django admin theme framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sundaradh/django-spectra",
    packages=find_packages(exclude=["example_project*", "tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Django>=4.2",
        "Pillow>=9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "black>=23.0",
            "flake8>=6.0",
            "isort>=5.12",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="django admin theme dashboard ui tailwind bootstrap modern",
    project_urls={
        "Bug Reports": "https://github.com/sundaradh/django-spectra/issues",
        "Source": "https://github.com/sundaradh/django-spectra",
        "Documentation": "https://django-spectra.readthedocs.io/",
    },
)
