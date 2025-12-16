from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="budgetnlp",
    version="0.0.1",
    description="NLP on a budget",
    packages=find_packages(),
    install_requires=['flashtext'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT"
)