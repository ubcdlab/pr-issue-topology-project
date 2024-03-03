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

manually_verified = [
    "MithrilJS-mithril.js-1645939388.html",
    "mlflow-mlflow-1655337135.html",
    "Rapptz-discord.py-1617112879.html",
    "MithrilJS-mithril.js-1652713638.html",
    "mlflow-mlflow-1635821214.html",
    "mlflow-mlflow-1656691361.html",
    "jupyterhub-jupyterhub-1519952687.html",
    "deployphp-deployer-1646371332.html",
    "TypeStrong-ts-node-1655499400.html",
    "mlflow-mlflow-1642514591.html",
    "pagekit-pagekit-1406249922.html",
    "App-vNext-Polly-1656194563.html",
    "jupyterhub-jupyterhub-1657795356.html",
    "apache-dubbo-1653940129.html",
    "rematch-rematch-1515402839.html",
    "pagekit-pagekit-1406249922.html",
]


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
                    [
                        root.replace(rootdir, "") + "_" + str(counter.get(root)),
                        rel_path,
                        file,
                    ]
                )

    verified = defaultdict(list)
    if len(workflow_types["Duplicate Issue Hub"]):
        verified["Duplicate Issue Hub"] = workflow_types["Duplicate Issue Hub"]
    if len(workflow_types["Divergent PR"]):
        verified["Divergent PR"] = workflow_types["Divergent PR"]
    for key in [
        "Competing PRs",
        "Extended PRs",
        "Decomposed Issue",
        "Dependent PRs",
        "Consequent Issue",
        "Consequent Issue PRs",
        "Integrating PR Hub",
    ]:
        verified[key] = list(
            filter(lambda x: x[2] in manually_verified, workflow_types[key])
        )
        if len(verified[key]) == 0:
            del verified[key]

    del workflow_types["Duplicate Issue Hub"]
    del workflow_types["Divergent PR"]
    for key in [
        "Competing PRs",
        "Extended PRs",
        "Decomposed Issue",
        "Dependent PRs",
        "Consequent Issue",
        "Consequent Issue PRs",
        "Integrating PR Hub",
    ]:
        workflow_types[key] = list(
            filter(lambda x: x[2] not in manually_verified, workflow_types[key])
        )
        if len(workflow_types[key]) == 0:
            del workflow_types[key]

    with open("interactive_html/template.html", "r") as x:
        t = Template("\n".join(x.readlines()))

    with open(f"interactive_html/repos/{repo.replace('/','-')}.html", "w") as x:
        x.write(
            t.render(
                repo=repo,
                unverified_workflow_types=workflow_types,
                verified_workflow_types=verified,
                last_updated=most_recently_updated,
            )
        )


if __name__ == "__main__":
    main()
