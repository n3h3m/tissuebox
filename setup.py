from distutils.core import setup

with open("pypi.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='tissuebox',
    version='18.12.12',
    description='Tissuebox :: Pythonic payload validator',
    author='nehem',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author_email='nehemiah.jacob@gmail.com',
    url='https://github.com/nehemiahjacob/tissuebox.git',
    packages=['tissuebox']
)
