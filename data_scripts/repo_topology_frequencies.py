from collections import defaultdict
from dataclasses import dataclass
from os.path import isdir
from statistics import mean, pstdev
from typing import List, Set
from click import command, option
import networkx as nx
from prettytable import PrettyTable
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from random import sample
from sys import path
from os import scandir, remove


path.append("..")

from data_scripts.helpers import generate_image, fetch_path, to_json


@command()
@option("--cypher", "cypher_path")
@option("--latex", "latex", is_flag=True, default=False)
def main(cypher_path: str, latex: bool):
    command = open(cypher_path, "r").read()

    def run_command(tx):
        result = tx.run(command)
        records = list(result)
        summary = result.consume()
        return records, summary

    with open("generate_neo4j_images/password", "r") as x:
        password = x.readline().strip()
    db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    session = db.session(database="neo4j")
    records, _ = session.execute_read(run_command)

    repo_to_matches_map = defaultdict(int)
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        repo = cypher_nodes[0]._properties["repository"]
        repo_to_matches_map[repo] += 1

    repo_to_matches_map = dict(
        sorted(
            repo_to_matches_map.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    )
    table = PrettyTable()
    table.field_names = ["Repository", "Matches", "Z-Score"]
    mean_matches = mean(repo_to_matches_map.values())
    stdev_matches = pstdev(repo_to_matches_map.values())
    for repo, matches in repo_to_matches_map.items():
        table.add_row([repo, matches, f"{(matches - mean_matches)/stdev_matches:.2f}"])
    print(table)
    print(sum(repo_to_matches_map.values()))
    if latex:
        print(table.get_latex_string())

    session.close()
    db.close()


if __name__ == "__main__":
    main()
