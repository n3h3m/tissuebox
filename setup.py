from distutils.core import setup

try:
    fh = open("pypi.rst", "r")
    long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="tissuebox",
    version="25.01.04",
    description="Tissuebox :: Pythonic payload validator",
    author="nehemiah",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author_email="nehemiah@skytechlabs.com.au",
    url="https://github.com/nehemiahjacob/tissuebox.git",
    packages=["tissuebox"],
)
