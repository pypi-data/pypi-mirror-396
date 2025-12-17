from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tumeryk_guardrails",
    version="0.2.9",
    author="Tumeryk",
    author_email="support@tumeryk.com",
    description="API Client for Tumeryk_Guardrails",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "aiohttp",
    ],
) 