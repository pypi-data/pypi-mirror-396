from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PACKAGE_NAME = "run_tracker"

setup(
    name=PACKAGE_NAME,
    version="0.1.3",
    author="Dominik Domiter",
    author_email="dominik.domiter@autowallis.hu",
    description="A lightweight SQLite-based run tracker for Python scripts with automatic logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/domiterd/{PACKAGE_NAME}",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
        ],
    },
    keywords="logging tracking sqlite scheduler monitoring execution",
    project_urls={
        "Bug Reports": f"https://github.com/domiterd/{PACKAGE_NAME}/issues",
        "Source": f"https://github.com/domiterd/{PACKAGE_NAME}",
    },
)

# HASZNÁLAT UTÁN:
# pip install run_tracker
# vagy
# pip install flow-execution-tracker
# stb.