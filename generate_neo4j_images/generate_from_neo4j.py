from click import command, option
import networkx as nx
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt


@command()
@option("--cypher", "cypher_path")
def main(cypher_path: str):
    command = open(cypher_path, "r").read()

    def run_command(tx):
        result = tx.run(command)
        records = list(result)
        summary = result.consume()
        return records, summary

    def generate_image(graph: nx.DiGraph, id: int, repo: str):
        pos = nx.nx_agraph.graphviz_layout(graph)
        types = nx.get_node_attributes(graph, "type")
        numbers = nx.get_node_attributes(graph, "number")
        statuses = nx.get_node_attributes(graph, "status")
        highlights = nx.get_node_attributes(graph, "to_highlight")
        labels = dict()
        edge_labels = dict()
        colors = []
        if graph.size() >= 10:
            plt.figure(1, figsize=(15, 15), dpi=120)
        else:
            plt.figure(1, figsize=(10, 10))
        plt.title(f"From {repo}:")
        issues = list(filter(lambda cn: types[cn] == "issue", graph.nodes))
        prs = list(filter(lambda cn: types[cn] == "pull_request", graph.nodes))
        issue_colors = [
            "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77"
            for cn in issues
        ]
        issue_edge_colors = ["#fede00" if highlights[cn] else issue_colors[i] for i, cn in enumerate(issues)]
        pr_colors = [
            "#f46d75" if statuses[cn] == "closed" else "#9d78cf" if statuses[cn] == "merged" else "#77dd77"
            for cn in prs
        ]
        pr_edge_colors = ["#fede00" if highlights[cn] else pr_colors[i] for i, cn in enumerate(prs)]
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
        edge_colors = ["#fede00" if graph[u][v]["to_highlight"] else "#000000" for u, v in graph.edges]
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
    # TODO: randomize
    for i, record in tqdm(enumerate(records), total=len(records)):
        to_highlight = [record.get("i")._properties["number"]]
        to_highlight += [pr._properties["number"] for pr in record.get("pull_requests")]
        cypher_nodes = record.get("nodes")
        cypher_edges = record.get("relationships")
        g = nx.DiGraph()
        nodes = [
            (
                n._properties["number"],
                {
                    "type": n._properties["type"],
                    "status": n._properties["status"],
                    "number": n._properties["number"],
                    "to_highlight": n._properties["number"] in to_highlight,
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
                    "to_highlight": e.nodes[0]._properties["number"] in to_highlight
                    and e.nodes[1]._properties["number"] in to_highlight,
                },
            )
            for e in cypher_edges
        ]
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        repo = cypher_nodes[0]._properties["repository"]
        generate_image(g, i, repo)

        break

    session.close()
    db.close()


if __name__ == "__main__":
    main()
