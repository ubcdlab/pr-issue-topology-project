from os.path import isfile
from pickle import load
from prettytable import PrettyTable
from click import command, option


@command()
@option("--size", "size", default=5)
@option("--write", "to_write", default=False, is_flag=True)
@option("--edge-direction", "edge_direction", default=False, is_flag=True)
def main(size: int, to_write: bool, edge_direction: bool):
    if to_write:
        print("Writing to file...")

    if not isfile(f"pattern_dump/{size}{'_undirected' if not edge_direction else ''}.pk"):
        print("Please run generate_all_patterns_of_size.py before this.")
        exit(1)

    with open(f"pattern_dump/{size}{'_undirected' if not edge_direction else ''}.pk", "rb") as x:
        all_patterns = load(x)

    total_patterns = sum(all_patterns.values())
    top_20_patterns = sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:20]

    table = PrettyTable()
    table.field_names = ["Pattern #", "Absolute Count", "Frequency of Size"]
    for i in range(len(top_20_patterns)):
        table.add_row([i, top_20_patterns[i][1], f"{top_20_patterns[i][1] / total_patterns:.2%}"])
    print(table)

    if to_write:
        with open(f"image_dump/{'undirected_' if not edge_direction else ''}{size}/patterns.txt", "w") as x:
            x.write(str(table))


main()
