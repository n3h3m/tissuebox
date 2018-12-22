from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tissuebox',
    version='18.12.7',
    description='Tissuebox :: Pythonic payload validator',
    author='nehem',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='nehemiah.jacob@gmail.com',
    url='https://github.com/nehemiahjacob/tissuebox.git',
    packages=['tissuebox']
)
