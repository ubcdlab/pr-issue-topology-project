from os.path import isfile
from sys import argv
from pickle import load
from prettytable import PrettyTable

size = 5
for arg in argv:
    if arg.startswith("size"):
        size = int(arg.split("=")[-1])

if not isfile(f"pattern_dump/{size}.pk"):
    print("Please run generate_all_patterns_of_size.py before this.")
    exit(1)

with open(f"pattern_dump/{size}.pk", "rb") as x:
    all_patterns = load(x)

total_patterns = sum(all_patterns.values())
top_20_patterns = sorted(all_patterns.items(), key=lambda x: x[1], reverse=True)[:20]

table = PrettyTable()
table.field_names = ["Pattern #", "Absolute Count", "Frequency of Size"]
for i in range(20):
    table.add_row([i, top_20_patterns[i][1], f"{top_20_patterns[i][1] / total_patterns:.2%}"])
print(table)
