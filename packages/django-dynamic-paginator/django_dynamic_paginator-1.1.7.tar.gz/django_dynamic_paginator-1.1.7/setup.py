from setuptools import setup, find_packages
import os

# Leer README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer requirements.txt
def read_requirements():
    with open("requirements.txt", "r") as req:
        return [line.strip() for line in req if line.strip() and not line.startswith("#")]

setup(
    name="django-dynamic-paginator",
    version="1.1.7",  # Versión corregida
    author="Jorge Luis de la Cruz",
    author_email="jorgeluisdcl30@gmail.com",
    description="Paginador dinámico avanzado para Django REST Framework con optimizaciones automáticas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/django-dynamic-paginator",
    project_urls={
        "Bug Tracker": "https://github.com/tuusuario/django-dynamic-paginator/issues",
        "Documentation": "https://github.com/tuusuario/django-dynamic-paginator#readme",
        "Source Code": "https://github.com/tuusuario/django-dynamic-paginator",
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
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=0.991",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "coverage>=6.0",
        ]
    },
    keywords="django djangorestframework pagination dynamic filtering optimization",
    include_package_data=True,
    zip_safe=False,
)