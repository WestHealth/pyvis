## Pyvis - a Python library for visualizing networks

## Description
Pyvis is built around [visjs](http://visjs.org/), a JavaScript visualization library.

## Documentation
Pyvis' full documentation can be found at http://something.foo

## Installation
You can install pyvis through pip:

```bash
pip install pyvis
```
Or if you have an archive of the project simply run the following from the top level directory:

```bash
python setup.py install
```

## Dependencies
[networkx](https://networkx.github.io/)

[jinja2](http://jinja.pocoo.org/)

[ipython](https://ipython.org/ipython-doc/2/install/install.html)

## Quick Start
The most basic use case of a pyvis instance is to create a Network object and invoke methods:

```python
from pyvis.network import Network

g = Network()
g.add_node(0)
g.add_node(1)
g.add_edge(0, 1)
g.show("basic.html")
```