from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

package_info = {}
with open("src/usdm4_pj/__info__.py") as fp:
    exec(fp.read(), package_info)

setup(
    name="usdm4_pj",
    version=package_info["__package_version__"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "usdm4>=0.14.0",
        "python-dateutil",
        "simple_error_log>=0.6.0",
    ],
    author="Johannes Ulander",
    author_email="",
    description="A package for processing USDM v4 protocol documents and converting them to a simplified patient format",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    tests_require=[
        "anyio",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "python-dotenv",
        "ruff",
    ],
    python_requires=">=3.12",
)
