from distutils.core import setup
try:
    fh = open("pypi.rst", "r")
    long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name='tissuebox',
    version='2019.01.17',
    description='Tissuebox :: Pythonic payload validator',
    author='nehem',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author_email='nehemiah.jacob@gmail.com',
    url='https://github.com/nehemiahjacob/tissuebox.git',
    packages=['tissuebox']
)
