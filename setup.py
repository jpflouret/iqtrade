from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="iqtrade",
    version="0.0.3",
    author="JP Flouret",
    author_email="jpflouret@gmail.com",
    description="Python wrapper around Questrade IQ API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpflouret/iqtrade",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.9",
)
