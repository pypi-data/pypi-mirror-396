from setuptools import setup, find_packages

setup(
    name="lam-middleware",
    version="0.1.0",
    packages=find_packages(),    
    author="Rohan Varma",
    description="Lightweight API Monitoring middleware for Starlette/FastAPI",
    install_requires=[
        "starlette>=0.27,<1.0",
        "httpx>=0.24,<1.0",
    ],
    python_requires=">=3.9",
)