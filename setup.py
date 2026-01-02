from setuptools import setup

try:
    fh = open("pypi.rst", "r")
    long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="tissuebox",
    version="26.1.1",
    description="Tissuebox :: Pythonic payload validator",
    author="nehemiah",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author_email="nehemiah@gmail.com",
    url="https://github.com/n3h3m/tissuebox.git",
    packages=["tissuebox"],
)
