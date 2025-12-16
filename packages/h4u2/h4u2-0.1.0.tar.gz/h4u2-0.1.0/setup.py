from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="h4u2",
    version="0.1.0",
    author="JI",
    packages=find_packages(), 
#    author_email="not needed?"
    description="A sample Python package for demonstration",
    long_description=long_description,
    long_description_content_type="text/markdown",
#    url="miweb.com",
)