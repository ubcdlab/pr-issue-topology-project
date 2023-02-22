from collections import defaultdict
from click import command, option
import networkx as nx
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from random import sample
from sys import path
from prettytable import PrettyTable


path.append("..")

from scripts.helpers import generate_image


class HashableDiGraph(nx.DiGraph):
    def __hash__(self):
        return int(nx.weisfeiler_lehman_graph_hash(self), base=16)

    def __eq__(self, other):
        return nx.weisfeiler_lehman_graph_hash(self) == nx.weisfeiler_lehman_graph_hash(other)


@command()
@option("--cypher", "cypher_path")
@option("--name", "query_name")
def main(cypher_path: str, query_name: str):
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
    records, summary = session.execute_read(run_command)

    graph_to_highlight_map = {}
    graph_to_edges_highlight_map = {}
    size_counts_map = defaultdict(int)
    graph_to_central_map = {}
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_edges = record.get("relationships")
        hl_map = defaultdict(int)
        g = HashableDiGraph(repo=cypher_nodes[0]._properties["repository"])
        nodes = [
            (
                n._properties["number"],
                {
                    "type": n._properties["type"],
                    "status": n._properties["status"],
                    "number": n._properties["number"],
                },
            )
            for n in cypher_nodes
        ]
        edges = [
            (
                e.nodes[0]._properties["number"],
                e.nodes[1]._properties["number"],
                {
                    "link_type": e._properties["labels"],
                },
            )
            for e in cypher_edges
        ]
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        for key in record.keys():
            if key == "central":
                graph_to_central_map[g] = record.get(key)._properties["number"]
                continue
            if key != "nodes" and key != "relationships":
                if type(record.get(key)) != list:
                    hl_map[record.get(key)._properties["number"]] = int(key.split("_")[-1])
                else:
                    for list_item in record.get(key):
                        hl_map[list_item._properties["number"]] = int(key.split("_")[-1])
        if g in graph_to_highlight_map:
            for key in hl_map:
                graph_to_highlight_map[g][key] = hl_map[key]
            continue
        else:
            graph_to_highlight_map[g] = {}
            for key in hl_map:
                graph_to_highlight_map[g][key] = hl_map[key]
        graph_to_edges_highlight_map[g] = [
            (
                e.nodes[0]._properties["number"],
                e.nodes[1]._properties["number"],
                graph_to_highlight_map[g][e.nodes[0]._properties["number"]],
            )
            for e in cypher_edges
            if e.nodes[0]._properties["number"] in graph_to_highlight_map[g]
        ]

    to_sample = min(len(records) // 2, 20)
    for i, graph in tqdm(
        enumerate(sample(list(graph_to_highlight_map.keys()), to_sample)),
        total=len(graph_to_highlight_map),
        leave=False,
    ):
        generate_image(
            graph,
            i,
            f"{query_name.capitalize()} topology\nFrom {graph.graph['repo']}:",
            15 if graph.size() >= 10 else 10,
            f"generate_neo4j_images/images/{query_name}/",
            dpi=120 if graph.size() >= 10 else 100,
            to_highlight=graph_to_highlight_map[graph],
            relationships_to_highlight=graph_to_edges_highlight_map[graph],
            node_size=250,
            central=graph_to_central_map[graph],
        )

    session.close()
    db.close()


if __name__ == "__main__":
    main()
