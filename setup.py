from setuptools import setup, find_packages

exec(open('pyvis/_version.py').read())
setup(
    name="pyvis",
    version=__version__,
    description="A Python network graph visualization library",
    long_description='Pyvis is a wrapper around visjs, a JavaScript network graph visualization library.',
    url="https://github.com/WestHealth/pyvis",
    author="Jose Unpingco",
    author_email="jhunpingco@westhealth.org",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2 >= 2.9.6",
        "networkx >= 1.11",
        "ipython >= 5.3.0",
        "jsonpickle >= 1.4.1"
    ]
)
