from collections import defaultdict
from os import walk
from re import compile
from os.path import isdir, join
from typing import List
from click import command, option
import networkx as nx
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from random import sample
from os import makedirs, scandir, remove
from jinja2 import Template


@command()
@option("--repo", "repo")
def main(repo: str):
    # jinja template select
    rootdir = "interactive_html/embeddable/"
    regex = compile(f"^{repo.replace('/','-')}-\\d+.html")

    workflow_types = defaultdict(list)
    for root, dirs, files in walk(rootdir):
        for file in files:
            if regex.match(file):
                workflow_types[
                    root.replace(rootdir, "").replace("_", " ").capitalize()
                ].append(
                    [file, "../" + join(root.replace("interactive_html/", ""), file)]
                )

    with open("interactive_html/template.html", "r") as x:
        t = Template("\n".join(x.readlines()))

    with open(f"interactive_html/repos/{repo.replace('/','-')}.html", "w") as x:
        x.write(t.render(repo=repo, workflow_types=workflow_types))


if __name__ == "__main__":
    main()
