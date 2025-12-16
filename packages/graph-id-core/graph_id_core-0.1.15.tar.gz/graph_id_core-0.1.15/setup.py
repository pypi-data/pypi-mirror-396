# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graph_id',
 'graph_id.analysis',
 'graph_id.app',
 'graph_id.commands',
 'graph_id.core']

package_data = \
{'': ['*']}

install_requires = \
['pybind11==2.11.1', 'pymatgen>=2025.10.7,<2026.0.0', 'scikit-learn>=0.24.1']

setup_kwargs = {
    'name': 'graph-id-core',
    'version': '0.1.15',
    'description': '',
    'long_description': '[![PyPI version](https://img.shields.io/pypi/v/graph-id-core.svg)](https://pypi.org/project/graph-id-core/)\n[![Python versions](https://img.shields.io/pypi/pyversions/graph-id-core.svg)](https://pypi.org/project/graph-id-core/)\n[![codecov](https://codecov.io/gh/kmu/graph-id-core/graph/badge.svg?token=AE2JIT3BAX)](https://codecov.io/gh/kmu/graph-id-core)\n\n# Graph ID\n\nGraph ID is a universal identifier system for atomistic structures including crystals and molecules. It generates unique, deterministic identifiers based on the topological and compositional properties of atomic structures, enabling efficient structure comparison, database indexing, and materials discovery.\n\n## Overview\n\nGraph ID works by:\n1. Converting atomic structures into graph representations where atoms are nodes and bonds are edges\n2. Analyzing the local chemical environment around each atom using compositional sequences\n3. Computing a hash-based identifier that captures both topology and composition\n4. Supporting various modes including topology-only comparisons and Wyckoff position analysis\n\n\n## Features\n\n- **Universal Structure Identification**: Generate unique IDs for any crystal or molecular structure\n- **Topological Analysis**: Option to generate topology-only IDs for structure type comparison\n- **Wyckoff Position Support**: Include crystallographic symmetry information in ID generation\n- **Distance Clustering**: Advanced clustering-based analysis for complex structures\n- **C++ Performance**: High-performance C++ backend with Python bindings\n- **Multiple Neighbor Detection**: Support for various neighbor-finding algorithms (MinimumDistanceNN, CrystalNN, etc.)\n\n## Installation\n\n### From PyPI\n\n```bash\npip install graph-id-core\npip install graph-id-db  # optional database component\n```\n\n### From Source\n\n```bash\ngit clone https://github.com/kmu/graph-id-core.git\ncd graph-id-core\ngit submodule update --init --recursive\npip install -e .\n```\n\n## Quick Start\n\n### Basic Usage\n\n```python\nfrom pymatgen.core import Structure, Lattice\nfrom graph_id import GraphIDMaker\n\n# Create a structure (NaCl)\nstructure = Structure.from_spacegroup(\n    "Fm-3m",\n    Lattice.cubic(5.692),\n    ["Na", "Cl"],\n    [[0, 0, 0], [0.5, 0.5, 0.5]]\n)\n\n# Generate Graph ID\nmaker = GraphIDMaker()\ngraph_id = maker.get_id(structure)\nprint(graph_id)  # Output: NaCl-88c8e156db1b0fd9\n```\n\n### Loading from Files\n\n```python\nfrom pymatgen.core import Structure\nfrom graph_id_cpp import GraphIDGenerator\n\n# Load structure from file\nstructure = Structure.from_file("path/to/structure.cif")\ngenerator = GraphIDGenerator()\ngraph_id = generator.get_id(structure)\n```\n\n### Advanced Configuration\n\n```python\nfrom graph_id_cpp import GraphIDGenerator\nfrom pymatgen.analysis.local_env import CrystalNN\n\n# Topology-only comparison (ignores composition)\ntopo_gen = GraphIDGenerator(topology_only=True)\ntopo_id = topo_gen.get_id(structure)\n\n# Include Wyckoff positions\nwyckoff_gen = GraphIDGenerator(wyckoff=True)\nwyckoff_id = wyckoff_gen.get_id(structure)\n\n# Use different neighbor detection\ncrystal_gen = GraphIDGenerator(nn=CrystalNN())  # Faster CrystalNN using C++ is also available\ncrystal_id = crystal_gen.get_id(structure)\n\n```\n\n### Search Structures from Database\n\nUse `graph-id-db` to search structures in the Materials Project using precomputed Graph ID stored in `graph-id-db`\n\n```python\n# pip install graph-id-db\nfrom graph_id_cpp import GraphIDGenerator\n\nfrom pymatgen.core import Structure, Lattice\n\nstructure = Structure.from_spacegroup(\n    "Fm-3m",\n    Lattice.cubic(5.692),\n    ["Na", "Cl"],\n    [[0, 0, 0], [0.5, 0.5, 0.5]]\n).get_primitive_structure()\ngen = GraphIDGenerator()\ngraph_id = gen.get_id(structure)\nprint(f"Graph ID of NaCl is {graph_id}")\n\nfrom graph_id_db import Finder\n\n# Search for structures in graph-id-db using GraphID\nfinder = Finder()\nfinder.find(graph_id)\n```\n\n## Examples\n\nMore comprehensive examples can be found in the [`tests/`](tests/) and [`examples/`](examples/) directories.\n\n## Applications\n\nGraph ID is particularly useful for:\n\n- **Materials Databases**: Efficient indexing and deduplication of structure databases\n- **High-throughput Screening**: Rapid identification of unique structures in computational workflows\n- **Polymorph Identification**: Distinguishing between different polymorphs of the same composition\n\n## Web Service (experimental)\n\nYou can search materials using Graph ID at [matfinder.net](https://matfinder.net).\n\n## Developer\'s notes\n\nThis repo is managed by `poetry`.\n\n### Installation\n\n1. Clone the repository:\n```bash\ngit clone https://github.com/kmu/graph-id-core.git\ncd graph-id-core\n```\n\n2. Initialize git submodules (required for the C++ build):\n```bash\ngit submodule update --init --recursive\n```\n\n3. Install the package and dependencies using Poetry:\n```bash\npoetry install\n```\n\n4. Install `pre-commit`\n```bash\npre-commit install\n```\n\n**Note:** The git submodules (`library/pybind11`, `library/eigen`, `library/gtl`) are required for building the C++ extension. Without them, the installation will fail during the CMake build step.\n\n### Testing\n\n```\npoetry run pytest\n```\n\nIf you have made changes to the C++ code, run `poetry run pip install -e --force-reinstall` to apply the changes before running the tests.\n\n### Releasing\n',
    'author': 'Koki Muraoka',
    'author_email': 'muraok_k@chemsys.t.u-tokyo.ac.jp',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.14',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
