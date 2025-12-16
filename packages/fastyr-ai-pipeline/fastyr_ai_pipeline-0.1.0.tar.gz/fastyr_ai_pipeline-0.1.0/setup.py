from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="fastyr-ai-pipeline",
    version="0.1.0",
    author="William Jefferson Mensah",
    author_email="mensahjefferson69@gmail.com",
    description="A flexible AI pipeline for STT, LLM, and TTS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cuuj69/fastyr",
    license="MIT",
    license_files=[],  # Prevent automatic license file detection to avoid metadata issues
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "sqlalchemy[asyncio]>=1.4.0",
        "alembic>=1.7.0",
        "strawberry-graphql>=0.96.0",
        "sentry-sdk>=1.5.0",
        "structlog>=21.1.0",
        "dependency-injector>=4.39.1",
        "python-jose[cryptography]>=3.3.0",
        "passlib>=1.7.4",
        "python-multipart>=0.0.5",
        "asyncpg>=0.25.0",
        "prometheus-client>=0.12.0",
        "gunicorn>=20.1.0",
        "psycopg2-binary>=2.9.1",
        "aiosqlite>=0.17.0",
        "aiofiles>=23.2.1",
        "PyJWT>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "coverage>=7.2.0",
            "httpx>=0.24.0",
            "aiohttp>=3.8.0",
            "pytest-env>=1.0.0",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
)
