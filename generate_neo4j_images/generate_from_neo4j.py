from typing import List
from click import command, option
import networkx as nx
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from dataclasses import dataclass
from random import sample


class HashableDiGraph(nx.DiGraph):
    def __hash__(self):
        return int(nx.weisfeiler_lehman_graph_hash(self), base=16)

    def __eq__(self, other):
        return nx.weisfeiler_lehman_graph_hash(self) == nx.weisfeiler_lehman_graph_hash(other)


@command()
@option("--cypher", "cypher_path")
def main(cypher_path: str):
    command = open(cypher_path, "r").read()

    def run_command(tx):
        result = tx.run(command)
        records = list(result)
        summary = result.consume()
        return records, summary

    def generate_image(graph: HashableDiGraph, id: int, hl_info: List[int]):
        pos = nx.nx_agraph.graphviz_layout(graph)
        types = nx.get_node_attributes(graph, "type")
        numbers = nx.get_node_attributes(graph, "number")
        statuses = nx.get_node_attributes(graph, "status")
        labels = dict()
        edge_labels = dict()
        colors = []
        if graph.size() >= 10:
            plt.figure(1, figsize=(15, 15), dpi=120)
        else:
            plt.figure(1, figsize=(10, 10))
        plt.title(f"From {graph.graph['repo']}:")
        issues = list(filter(lambda cn: types[cn] == "issue", graph.nodes))
        prs = list(filter(lambda cn: types[cn] == "pull_request", graph.nodes))
        issue_colors = [
            "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77"
            for cn in issues
        ]
        issue_edge_colors = ["#fede00" if numbers[cn] in hl_info else issue_colors[i] for i, cn in enumerate(issues)]
        pr_colors = [
            "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77"
            for cn in prs
        ]
        pr_edge_colors = ["#fede00" if numbers[cn] in hl_info else pr_colors[i] for i, cn in enumerate(prs)]
        nx.draw(
            graph,
            pos,
            nodelist=issues,
            node_color=issue_colors,
            edgecolors=issue_edge_colors,
            node_shape="s",
            font_size=10,
            node_size=250,
        )
        nx.draw(
            graph,
            pos,
            nodelist=prs,
            node_color=pr_colors,
            edgecolors=pr_edge_colors,
            node_shape="o",
            font_size=10,
            node_size=250,
        )
        for cn in graph.nodes:
            labels[cn] = f"{'I' if types[cn] == 'issue' else 'PR'} #{numbers[cn]}"
        link_types = nx.get_edge_attributes(graph, "link_type")
        edge_colors = [
            "#fede00" if numbers[u] in hl_info and numbers[v] in hl_info else "#000000" for u, v in graph.edges
        ]
        for ce in graph.edges:
            if link_types[ce] != "other":
                edge_labels[ce] = link_types[ce]
        nx.draw_networkx_labels(graph, pos=pos, labels=labels, font_size=10)
        nx.draw_networkx_edges(graph, pos, edge_color=edge_colors)
        nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels, font_size=10)
        plt.tight_layout()
        plt.savefig(f"generate_neo4j_images/images/{id}.png")
        plt.clf()

    with open("generate_neo4j_images/password", "r") as x:
        password = x.readline().strip()
    db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    session = db.session(database="neo4j")
    records, summary = session.execute_read(run_command)

    graph_to_highlight_map = {}
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_edges = record.get("relationships")
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
        # TODO: make more general
        to_highlight = [record.get("i")._properties["number"]]
        to_highlight += [pr._properties["number"] for pr in record.get("pull_requests")]
        if g in graph_to_highlight_map:
            graph_to_highlight_map[g] += to_highlight
            continue
        graph_to_highlight_map[g] = to_highlight

    to_sample = min(len(records) // 2, 20)
    for i, graph in tqdm(
        enumerate(sample(list(graph_to_highlight_map.keys()), to_sample)),
        total=len(graph_to_highlight_map),
        leave=False,
    ):
        image_hl_info = graph_to_highlight_map[graph]
        generate_image(graph, i, image_hl_info)

    session.close()
    db.close()


if __name__ == "__main__":
    main()
