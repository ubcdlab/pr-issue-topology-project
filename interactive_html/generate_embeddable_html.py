from collections import defaultdict
from os.path import isdir, dirname, abspath
from sys import path
from click import command, option
import networkx as nx
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from random import sample
from os import makedirs, scandir, remove
from bokeh.models import (
    GlobalInlineStyleSheet,
    HTMLLabelSet,
    MultiLine,
    OpenURL,
    Scatter,
    ColumnDataSource,
    TapTool,
    HoverTool,
    Legend,
)
from bokeh.io import output_file, save
from bokeh.plotting import figure, from_networkx

path.append(dirname(dirname(abspath(__file__))))


@command()
@option("--cypher", "cypher_path")
@option("--name", "query_name")
def main(cypher_path: str, query_name: str):
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
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_edges = record.get("relationships") + (
            record.get("match_relationships")
            if "match_relationships" in record.keys()
            else []
        )
        if "optional_r" in record.keys() and record.get("optional_r") is not None:
            cypher_edges += [record.get("optional_r")]
        to_highlight = []
        g = nx.Graph(repo=cypher_nodes[0]._properties["repository"], link=None)
        for key in record.keys():
            if key not in [
                "nodes",
                "relationships",
                "match_relationships",
                "all_ids",
                "optional_issue",
                "optional_r",
                "proportion",
            ] or (key == "optional_issue" and record.get(key) is not None):
                if type(record.get(key)) != list:
                    n = record.get(key)
                    to_highlight += [n._properties["number"]]
                    g.add_node(
                        n._properties["number"],
                        type=n._properties["type"],
                        status=n._properties["status"],
                        number=n._properties["number"],
                        url=n._properties["url"],
                        last_updated=n._properties["updated_at"],
                        title=(
                            n._properties["title"] if "title" in n._properties else ""
                        ),
                    )
                else:
                    to_highlight += [
                        list_item._properties["number"] for list_item in record.get(key)
                    ]
                    g.add_nodes_from(
                        [
                            (
                                n._properties["number"],
                                {
                                    "type": n._properties["type"],
                                    "status": n._properties["status"],
                                    "number": n._properties["number"],
                                    "url": n._properties["url"],
                                    "last_updated": n._properties["updated_at"],
                                    "title": (
                                        n._properties["title"]
                                        if "title" in n._properties
                                        else ""
                                    ),
                                },
                            )
                            for n in record.get(key)
                        ]
                    )
        nodes = [
            (
                n._properties["number"],
                {
                    "type": n._properties["type"],
                    "status": n._properties["status"],
                    "number": n._properties["number"],
                    "url": n._properties["url"],
                    "last_updated": n._properties["updated_at"],
                    "title": (
                        n._properties["title"] if "title" in n._properties else ""
                    ),
                },
            )
            for n in cypher_nodes
        ]
        edges = [
            (
                e.nodes[0]._properties["number"],
                e.nodes[1]._properties["number"],
                {
                    "title": e._properties["labels"],
                },
            )
            for e in cypher_edges
            if "number" in e.nodes[0]._properties and "number" in e.nodes[1]._properties
        ]
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        assert all([t in g.nodes() for t in to_highlight])
        edges_to_hl = []
        if "match_relationships" not in record.keys():
            edges_to_hl = [
                (e.nodes[0]._properties["number"], e.nodes[1]._properties["number"])
                for e in cypher_edges
                if e.nodes[0]._properties["number"] in to_highlight
                and e.nodes[1]._properties["number"] in to_highlight
            ]
        else:
            edges_to_hl = [
                (e.nodes[0]._properties["number"], e.nodes[1]._properties["number"])
                for e in (
                    record.get("match_relationships")
                    + (
                        [record.get("optional_r")]
                        if "optional_r" in record.keys()
                        and record.get("optional_r") is not None
                        else []
                    )
                )
                if "number" in e.nodes[0]._properties
                and "number" in e.nodes[1]._properties
            ]
        graph_to_edges_highlight_map[g] = edges_to_hl
        graph_to_highlight_map[g] = to_highlight

    # to_sample = min(len(records) // 2, 20)
    # to_sample = min(len(records), 40)  # sample more
    to_sample = len(records)
    if isdir(f"interactive_html/embeddable/{query_name}/"):
        for file in scandir(f"interactive_html/embeddable/{query_name}/"):
            remove(file.path)
    else:
        makedirs(f"interactive_html/embeddable/{query_name}/")
    for i, graph in tqdm(
        enumerate(sample(list(graph_to_highlight_map.keys()), to_sample)),
        total=to_sample,
        leave=False,
    ):

        numbers = nx.get_node_attributes(graph, "number")
        types = nx.get_node_attributes(graph, "type")
        statuses = nx.get_node_attributes(graph, "status")
        urls = nx.get_node_attributes(graph, "url")
        colors = {}
        descriptions = {}
        titles = nx.get_node_attributes(graph, "title")
        for cn in graph.nodes:
            colors[cn] = (
                (
                    "#f46d75"
                    if statuses[cn] == "closed"
                    else "#a57cde" if statuses[cn] == "merged" else "#77dd77"
                )
                if numbers[cn] in graph_to_highlight_map[graph]
                else (
                    "#f9b6ba"
                    if statuses[cn] == "closed"
                    else "#d2bdee" if statuses[cn] == "merged" else "#bbeebb"
                )
            )
            descriptions[cn] = (
                (
                    "Closed"
                    if statuses[cn] == "closed"
                    else "Merged" if statuses[cn] == "merged" else "Open"
                )
                + " "
                + ("PR" if types[cn] == "pull_request" else "Issue")
            )
        markers = {
            cn: "circle" if types[cn] == "pull_request" else "square" for cn in types
        }
        node_edges = {
            cn: "#0096FF" if numbers[cn] in graph_to_highlight_map[graph] else "#000000"
            for cn in numbers
        }
        node_opacity = {
            cn: 1 if numbers[cn] in graph_to_highlight_map[graph] else 0.5
            for cn in numbers
        }
        edge_edges = {
            (u, v): (
                "#0096FF"
                if (u, v) in graph_to_edges_highlight_map[graph]
                or (v, u) in graph_to_edges_highlight_map[graph]
                else "#000000"
            )
            for u, v in graph.edges
        }
        edges_opacity = {
            (u, v): (
                1
                if (u, v) in graph_to_edges_highlight_map[graph]
                or (v, u) in graph_to_edges_highlight_map[graph]
                else 0.4
            )
            for u, v in graph.edges
        }
        nx.set_node_attributes(graph, colors, "color")
        nx.set_node_attributes(graph, descriptions, "desc")
        nx.set_node_attributes(graph, markers, "marker")
        nx.set_node_attributes(graph, node_edges, "edge_color")
        nx.set_node_attributes(graph, node_opacity, "opacity")
        nx.set_edge_attributes(graph, edge_edges, "edge_color")
        nx.set_edge_attributes(graph, edges_opacity, "opacity")

        stylesheet = GlobalInlineStyleSheet(css="body {overflow:hidden}")
        plot = figure(
            tools="pan,wheel_zoom,box_zoom,reset,tap",
            active_drag="pan",
            active_scroll="wheel_zoom",
            toolbar_location=None,
            sizing_mode="stretch_both",
            stylesheets=[stylesheet],
        )
        plot.xaxis.major_label_text_font_size = "0pt"
        plot.xaxis.major_tick_line_color = None
        plot.xaxis.minor_tick_line_color = None
        plot.xaxis.axis_line_color = "#e5e5e5"
        plot.yaxis.major_label_text_font_size = "0pt"
        plot.yaxis.major_tick_line_color = None
        plot.yaxis.minor_tick_line_color = None
        plot.yaxis.axis_line_color = "#e5e5e5"
        plot.grid.grid_line_alpha = 0
        graph_plot = from_networkx(graph, nx.spring_layout, center=(0, 0))
        pos = graph_plot.layout_provider.graph_layout

        labels_dict = {}
        labels_dict["x"] = [pos[cn][0] for cn in pos]
        labels_dict["y"] = [pos[cn][1] for cn in pos]
        labels_dict["text"] = [
            f"{'Issue' if types[cn] == 'issue' else 'PR'} #{numbers[cn]}" for cn in pos
        ]
        labels_dict["text_size"] = [
            "24px" if numbers[cn] in graph_to_highlight_map[graph] else "16px"
            for cn in pos
        ]
        labels_dict["text_opacity"] = [
            1 if numbers[cn] in graph_to_highlight_map[graph] else 0.5 for cn in pos
        ]
        labels_dict["edge_color"] = [
            "#0096FF" if numbers[cn] in graph_to_highlight_map[graph] else "#000000"
            for cn in pos
        ]
        source = ColumnDataSource(labels_dict)
        labels = HTMLLabelSet(
            x="x",
            y="y",
            text="text",
            text_font_size="text_size",
            text_alpha="text_opacity",
            source=source,
            text_color="edge_color",
            text_align="center",
            text_baseline="top",
            y_offset=-15,
        )
        plot.renderers.append(labels)

        graph_plot.node_renderer.glyph = Scatter(
            size=20,
            fill_color="color",
            marker="marker",
            line_color="edge_color",
            line_alpha="opacity",
            line_width=3,
            tags=["link"],
        )
        graph_plot.edge_renderer.glyph = MultiLine(
            line_color="edge_color", line_width=2, line_alpha="opacity"
        )
        graph_plot.node_renderer.selection_glyph = graph_plot.node_renderer.glyph
        graph_plot.node_renderer.nonselection_glyph = graph_plot.node_renderer.glyph
        plot.renderers.append(graph_plot)

        taptool = plot.select(type=TapTool)
        taptool.callback = OpenURL(url="@url")

        titles_dict = {}
        titles_dict["title"] = [titles[cn] for cn in pos]
        titles_source = ColumnDataSource(titles_dict)
        plot.add_tools(
            HoverTool(
                tooltips=[
                    ("", "@title"),
                    ("", "@desc"),
                    ("", "Click to open GitHub URL"),
                ]
            )
        )

        most_recently_updated = max(
            nx.get_node_attributes(graph, "last_updated").values()
        )
        output_file(
            f"interactive_html/embeddable/{query_name}/{graph.graph['repo'].replace('/','-')}-{most_recently_updated}.html"
        )
        save(plot)

    session.close()
    db.close()


if __name__ == "__main__":
    main()
