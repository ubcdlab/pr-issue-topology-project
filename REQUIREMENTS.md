# Requirements

At least 4GB of RAM was required to run and configure Neo4j. Our artifacts will require ~5GB of storage if you choose to download additional raw data beyond the storage needed to download the repository and the tools. No particular operating system is required, but our scripts were tested on Linux (Manjaro and Ubuntu). See [requirements.txt](./requirements.txt) for a list of Python dependencies. Other dependencies that should be installed:

- [Python 3.11](https://www.python.org/) (with `python-dev`, `pip` and `venv`)
- [Neo4j Desktop 1.5.9 (server version 5.3.0)](https://neo4j.com/) with the [APOC 5.3.0 plugins](https://neo4j.com/labs/apoc/5/installation/)
- A reasonably up-to-date web browser (tested with Chrome 124 on Linux)
- Optionally, the IBM Plex Sans font for generating images (on Ubuntu, `sudo apt install fonts-ibm-plex`)

The VirtualBox image provided was tested with Ubuntu 20.04.6. On Ubuntu, you may need to additionally run `sudo apt install build-essential` in order to build the `pygraphviz` Python dependency in `requirements.txt`.
