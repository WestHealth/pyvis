from setuptools import setup, find_packages

setup(
    name="pyvis",
    version="0.1.4",
    description="A Python network visualization library",
    url="https://github.com/WestHealth/pyvis",
    author="Giancarlo Perrone",
    author_email="gperrone@westhealth.org",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jinja2 >= 2.9.6",
        "networkx >= 1.11",
        "ipython == 5.3.0"
    ]
)
