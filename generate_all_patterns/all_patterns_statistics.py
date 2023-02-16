from os import listdir
from re import match
from pickle import load
from dataclasses import dataclass
from prettytable import PrettyTable
from tqdm import tqdm
from click import command, option


@dataclass(repr=True)
class TopKPatternResult:
    size: int
    source_number: int
    percentage: float
    absolute_count: int


@command
@option("--percentage-ordering", "percentage_ordering", is_flag=True, default=False)
@option("--edge-direction", "edge_direction", is_flag=True, default=False)
@option("--all", "all_ordering", is_flag=True, default=False)
def main(percentage_ordering: bool, edge_direction: bool, all_ordering: bool):
    path_list = [
        "pattern_dump/" + f
        for f in listdir("pattern_dump")
        if match(rf"[0-9]+{'_undirected' if not edge_direction else ''}\.pk", f)
    ]

    all_patterns = {}

    for path in tqdm(path_list, total=len(path_list), leave=True):
        size = int(path.replace("pattern_dump/", "").replace("_undirected", "").split(".pk")[0])
        with open(path, "rb") as x:
            all_patterns_of_size = load(x)
            total_patterns = sum(all_patterns_of_size.values())
            top_20_patterns = sorted(all_patterns_of_size.items(), key=lambda x: x[1], reverse=True)
            for i, pattern in enumerate(top_20_patterns):
                all_patterns[pattern[0]] = TopKPatternResult(size, i, pattern[1] / total_patterns, pattern[1])

    all_patterns = list(
        map(
            lambda y: y[1],
            sorted(
                all_patterns.items(),
                key=lambda x: x[1].percentage if percentage_ordering else x[1].absolute_count,
                reverse=True,
            )[: 30 if not all_ordering else len(all_patterns.items())],
        )
    )

    table = PrettyTable()
    table.field_names = ["Frequency of Size", "Size", "Pattern #", "Absolute Count"]
    for pattern in all_patterns:
        table.add_row(
            [
                f"{pattern.percentage:.2%}",
                pattern.size,
                pattern.source_number,
                pattern.absolute_count,
            ]
        )
    print(table)


main()
