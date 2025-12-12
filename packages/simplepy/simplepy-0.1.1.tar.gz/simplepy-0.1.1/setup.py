from setuptools import setup, find_packages

setup(
    name="simplepy",          # name on PyPI, pip install simplepy
    version="0.1.1",          # change when you update
    packages=find_packages(), # will include the simplepy/ folder
    description="Your description here",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
)