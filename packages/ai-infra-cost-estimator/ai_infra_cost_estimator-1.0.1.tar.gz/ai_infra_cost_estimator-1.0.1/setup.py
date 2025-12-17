"""
AI Infra Cost Estimator - Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-infra-cost-estimator",
    version="1.0.0",
    author="MindTheInfraAI",
    author_email="",
    description="Estimate real-world AI + cloud costs before scaling breaks you",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MindTheInfraAI/AI_Infra_Cost_Estimator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-cost-estimator=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["pricing/*.json", "examples/*.yaml"],
    },
)
