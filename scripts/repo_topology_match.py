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

from scripts.helpers import generate_image, fetch_path, to_json


@dataclass(repr=True)
class MTOCStatistics:
    in_topology: Set
    matches: int
    graph_nodes: int


@command()
@option("--cypher", "cypher_path")
@option("--type", "node_type")
@option("--status", "node_status")
@option("--latex", "latex", is_flag=True, default=False)
@option("--integrating", "integrating", is_flag=True, default=False)
def main(cypher_path: str, node_type: str, node_status: str, latex: bool, integrating: bool):
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

    repo_to_matches_map = {}
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        repo = cypher_nodes[0]._properties["repository"]
        cypher_node_nums = list(map(lambda x: x._properties["number"], record.get("nodes")))
        graph = to_json(f"data/graph_{repo.replace('/','-')}.json")
        candidates = list(filter(lambda x: x["connected_component_size"][0] > 2, graph["nodes"]))
        if repo not in repo_to_matches_map:
            repo_to_matches_map[repo] = MTOCStatistics(set(), 0, len(candidates))
        repo_to_matches_map[repo].in_topology.update(
            list(
                map(
                    lambda x: x["id"],
                    filter(
                        lambda x: x["id"] in cypher_node_nums
                        and ((x["type"] == node_type and x["status"] == node_status) or integrating),
                        candidates,
                    ),
                )
            )
        )
        repo_to_matches_map[repo].matches += 1

    repo_to_matches_map = dict(
        sorted(
            repo_to_matches_map.items(),
            key=lambda x: len(x[1].in_topology) / x[1].graph_nodes,
            reverse=True,
        )
    )
    table = PrettyTable()
    table.field_names = ["Repository", "MTOC", "Matches"]
    for repo, mtoc in repo_to_matches_map.items():
        table.add_row([repo, f"{len(mtoc.in_topology) / mtoc.graph_nodes:.2%}", mtoc.matches])
    print(table)
    if latex:
        print(table.get_latex_string().replace("%", "\\%"))
    print(f"{mean(list(map(lambda x: len(x[1].in_topology) / x[1].graph_nodes, repo_to_matches_map.items()))):.2%}")
    print(f"{pstdev(list(map(lambda x: len(x[1].in_topology) / x[1].graph_nodes, repo_to_matches_map.items()))):.2%}")

    session.close()
    db.close()


if __name__ == "__main__":
    main()
