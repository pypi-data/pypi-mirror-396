from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

package_info = {}
with open("src/raw_docx/__info__.py") as fp:
    exec(fp.read(), package_info)

setup(
    name="raw_docx",
    version=package_info["__package_version__"],
    author="Dave Iberson-Hurst",
    author_email="",
    description="A package for processing and analyzing raw document formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daveih/raw_docx",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={},
    install_requires=["python-docx>=1.1.2", "simple_error_log>=0.6.0"],
    tests_require=["pytest", "pytest-cov", "pytest-mock", "python-dotenv", "pyyaml"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
