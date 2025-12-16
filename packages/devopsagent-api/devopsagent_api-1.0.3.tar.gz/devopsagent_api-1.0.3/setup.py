"""
Setup script for devopsagent-api package.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements (fallback for legacy builds)
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # When using pyproject.toml, dependencies are specified there
    requirements = []

setup(
    name="devopsagent-api",
    version="1.0.3",
    author="Stefan Saftic",
    author_email="stefan.saftic@gmail.com",
    description="Python client library for AWS DevOps Agent API using boto3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefansaftic/community-devops-agent",
    packages=find_packages(exclude=["tests*", "examples*"]),
    package_data={
        "devopsagent_api": [
            "data/community-devops-agent/2025-12-09/*.json",
            "data/community-aidevops/2018-05-10/*.json"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    keywords="aws devops agent boto3 api client",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=0.18.0",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/stefansaftic/community-devops-agent",
        "Documentation": "https://community-devops-agent.readthedocs.io/en/latest/",
        "Repository": "https://github.com/stefansaftic/community-devops-agent",
        "Issues": "https://github.com/stefansaftic/community-devops-agent/issues",
        "Changelog": "https://github.com/stefansaftic/community-devops-agent/blob/main/CHANGELOG.md",
    },
)
