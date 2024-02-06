from collections import Counter, defaultdict
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

    counter = Counter()
    workflow_types = defaultdict(list)
    most_recently_updated = None
    recently_updated_time = float("inf")
    for root, dirs, files in walk(rootdir):
        for file in files:
            if regex.match(file):
                counter.update({root: 1})
                rel_path = "../" + join(root.replace("interactive_html/", ""), file)
                last_updated = int(file.replace(".html", "").split("-")[-1])
                if last_updated < recently_updated_time:
                    recently_updated_time = last_updated
                    most_recently_updated = rel_path
                workflow_types[
                    root.replace(rootdir, "")
                    .replace("_", " ")
                    .title()
                    .replace("Pr", "PR")
                ].append(
                    [root.replace(rootdir, "") + "_" + str(counter.get(root)), rel_path]
                )

    with open("interactive_html/template.html", "r") as x:
        t = Template("\n".join(x.readlines()))

    with open(f"interactive_html/repos/{repo.replace('/','-')}.html", "w") as x:
        x.write(
            t.render(
                repo=repo,
                workflow_types=workflow_types,
                last_updated=most_recently_updated,
            )
        )


if __name__ == "__main__":
    main()
