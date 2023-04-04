from collections import defaultdict
from statistics import correlation
import matplotlib.pyplot as plt

from scripts.helpers import all_graphs, fetch_repo, to_json, num_graphs

with open("scripts/tableConvert.csv") as x:
    lines = x.readlines()
    lines = [l for l in lines if l.replace(",", "").strip()]

repo_to_matches_map = defaultdict(int)
for l in lines:
    lsplit = l.split(",")
    repo_to_matches_map[lsplit[0]] += int(lsplit[1])

repo_to_matches_map = dict(
    sorted(map(lambda x: [x[0].replace("/", "-"), x[1]], repo_to_matches_map.items()), key=lambda x: x[1], reverse=True)
)

size_to_matches_map = {}
for p in all_graphs():
    repo = fetch_repo(str(p), from_graph=True)
    size_to_matches_map[repo] = {
        len(to_json(str(p))["nodes"]): repo_to_matches_map[repo] if repo in repo_to_matches_map else 0.01
    }

size_to_matches_map = dict(sorted(size_to_matches_map.items(), key=lambda x: list(x[1].values())[0], reverse=True))

plt.figure(figsize=(8, 4))

font = {"fontname": "IBM Plex Sans"}
plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.xlabel("Number of Nodes (log scale)", **font)
plt.ylabel("Number of Workflow Type Matches (log scale)", **font)

ax = plt.gca()
ax.set_yscale("symlog")
ax.set_xscale("symlog")
ax.spines[["right", "top"]].set_visible(False)
legend = None
cmap = plt.cm.get_cmap("RdYlGn", num_graphs())
ax.set_axisbelow(True)
ax.yaxis.grid(True, zorder=-1, which="major", color="#ddd")
ax.xaxis.grid(True, zorder=-1, which="major", color="#ddd")
for i, data_dict in enumerate(size_to_matches_map.values()):
    x = data_dict.keys()
    y = data_dict.values()
    plt.scatter(x, y, color=cmap(i))
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
min_top = [
    plt.Line2D([0], [0], color="w", marker="o", markerfacecolor=cmap(i), label=x, markersize=8)
    for i, x in enumerate(list(size_to_matches_map.keys())[:5])
]
max_top = [
    plt.Line2D([0], [0], color="w", marker="o", markerfacecolor=cmap(num_graphs() - 5 + i), label=x, markersize=8)
    for i, x in enumerate(list(size_to_matches_map.keys())[-5:])
]
plt.legend(handles=min_top + max_top, loc="center left", bbox_to_anchor=(1, 0.5))

try:
    makedirs("misc_images/")
except:
    pass
plt.savefig(f"misc_images/repo_size_to_matches.png", bbox_inches="tight", dpi=150)
print(
    correlation(
        list(map(lambda x: list(x.keys())[0], size_to_matches_map.values())),
        list(map(lambda x: list(x.values())[0], size_to_matches_map.values())),
    )
)
