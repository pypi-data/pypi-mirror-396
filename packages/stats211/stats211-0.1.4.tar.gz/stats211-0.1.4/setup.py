from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stats211",
    version="0.1.4",
    author="Isaac Lagoy",
    author_email="isaacblagoy@gmail.com",
    description="Comprehensive statistical functions for hypothesis testing, confidence intervals, regression, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stats211",  # Update with your actual URL if you have one
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Education",
    ],
    keywords=["statistics", "hypothesis-testing", "confidence-intervals", "regression", "statistical-analysis"],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    include_package_data=True,
)
