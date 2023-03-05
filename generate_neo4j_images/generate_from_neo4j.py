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


@command()
@option("--cypher", "cypher_path")
@option("--name", "query_name")
@option("--size-distribution", "size_distribution", is_flag=True, default=False)
def main(cypher_path: str, query_name: str, size_distribution: bool):
    command = open(cypher_path, "r").read()

    def run_command(tx):
        result = tx.run(command, {"mode": "ids" if query_name == "pr_hub" else ""})
        records = list(result)
        summary = result.consume()
        return records, summary

    with open("generate_neo4j_images/password", "r") as x:
        password = x.readline().strip()
    db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    session = db.session(database="neo4j")
    records, _ = session.execute_read(run_command)

    graph_to_highlight_map = {}
    graph_to_edges_highlight_map = {}
    size_counts_map = defaultdict(int)
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_edges = (
            record.get("relationships") + record.get("match_relationships")
            if "match_relationships" in record.keys()
            else []
        )
        to_highlight = []
        g = nx.Graph(repo=cypher_nodes[0]._properties["repository"], link=None)
        for key in record.keys():
            if key != "nodes" and key != "relationships" and key != "match_relationships":
                if type(record.get(key)) != list:
                    n = record.get(key)
                    to_highlight += [n._properties["number"]]
                    g.graph["link"] = n._properties["url"]
                    g.add_node(
                        n._properties["number"],
                        type=n._properties["type"],
                        status=n._properties["status"],
                        number=n._properties["number"],
                    )
                else:
                    to_highlight += [list_item._properties["number"] for list_item in record.get(key)]
                    g.add_nodes_from(
                        [
                            (
                                n._properties["number"],
                                {
                                    "type": n._properties["type"],
                                    "status": n._properties["status"],
                                    "number": n._properties["number"],
                                },
                            )
                            for n in record.get(key)
                        ]
                    )
        if size_distribution:
            size_counts_map[len(to_highlight)] += 1
            continue
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
        assert all([t in g.nodes() for t in to_highlight])
        edges_to_hl = []
        if "match_relationships" not in record.keys():
            edges_to_hl = [
                (e.nodes[0]._properties["number"], e.nodes[1]._properties["number"])
                for e in cypher_edges
                if e.nodes[0]._properties["number"] in to_highlight and e.nodes[1]._properties["number"] in to_highlight
            ]
        else:
            edges_to_hl = [
                (e.nodes[0]._properties["number"], e.nodes[1]._properties["number"])
                for e in record.get("match_relationships")
            ]
        graph_to_edges_highlight_map[g] = edges_to_hl
        graph_to_highlight_map[g] = to_highlight

    if size_distribution:
        total = sum(size_counts_map.values())
        table = PrettyTable()
        table.field_names = ["Size", "Count", "Percentage of Total"]
        for k, v in sorted(size_counts_map.items(), key=lambda i: i[1], reverse=True):
            table.add_row([k, v, f"{v/total:.2%}"])
        print(table)
        print(f"Total matches: {total}")
        exit(0)

    to_sample = min(len(records) // 2, 20)
    for i, graph in tqdm(
        enumerate(sample(list(graph_to_highlight_map.keys()), to_sample)),
        total=to_sample,
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
            link=graph.graph["link"],
        )

    session.close()
    db.close()


if __name__ == "__main__":
    main()
