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
@option("--size-distribution", "size_distribution", is_flag=True, default=False)
def main(cypher_path: str, query_name: str, size_distribution: bool):
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
    size_counts_map = defaultdict(int)
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_edges = record.get("relationships")
        to_highlight = []
        for key in record.keys():
            if key != "nodes" and key != "relationships":
                if type(record.get(key)) != list:
                    to_highlight += [record.get(key)._properties["number"]]
                else:
                    to_highlight += [list_item._properties["number"] for list_item in record.get(key)]
        if size_distribution:
            size_counts_map[len(to_highlight)] += 1
            continue
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
        if g in graph_to_highlight_map:
            graph_to_highlight_map[g] += to_highlight
            continue
        graph_to_highlight_map[g] = to_highlight

    if size_distribution:
        total = sum(size_counts_map.values())
        table = PrettyTable()
        table.field_names = ["Size", "Count", "Percentage of Total"]
        for k, v in size_counts_map.items():
            table.add_row([k, v, f"{v/total:.2%}"])
        print(table)
        print(f"Total matches: {total}")
        exit(0)

    to_sample = min(len(records) // 2, 20)
    for i, graph in tqdm(
        enumerate(sample(list(graph_to_highlight_map.keys()), to_sample)),
        total=len(graph_to_highlight_map),
        leave=False,
    ):
        image_hl_info = graph_to_highlight_map[graph]
        generate_image(
            graph,
            i,
            f"{query_name.capitalize()} topology\nFrom {graph.graph['repo']}:",
            15 if graph.size() >= 10 else 10,
            f"generate_neo4j_images/images/{query_name}/",
            dpi=120 if graph.size() >= 10 else 100,
            to_highlight=graph_to_highlight_map[graph],
            node_size=250,
        )

    session.close()
    db.close()


if __name__ == "__main__":
    main()
