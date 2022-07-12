from setuptools import setup, find_packages, __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

exec(open('pyvis/_version.py').read())
setup(
    name="pyvis",
    version=__version__,
    description="A Python network graph visualization library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/WestHealth/pyvis",
    author="Jose Unpingco",
    author_email="datascience@westhealth.org",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2 >= 2.9.6",
        "networkx >= 1.11",
        "ipython >= 5.3.0",
        "jsonpickle >= 1.4.1"
    ],
    python_requires=">3.6",
)
