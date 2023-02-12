from os import listdir
from re import match
from pickle import load
from dataclasses import dataclass
from prettytable import PrettyTable


@dataclass(repr=True)
class TopKPatternResult:
    size: int
    source_number: int
    percentage: float
    absolute_count: int


path_list = ["pattern_dump/" + f for f in listdir("pattern_dump") if match(r"[0-9]+\.pk", f)]

all_patterns = {}

for path in path_list:
    size = int(path.replace("pattern_dump/", "").split(".pk")[0])
    with open(path, "rb") as x:
        all_patterns_of_size = load(x)
        total_patterns = sum(all_patterns_of_size.values())
        top_20_patterns = sorted(all_patterns_of_size.items(), key=lambda x: x[1], reverse=True)[:20]
        for i, pattern in enumerate(top_20_patterns):
            all_patterns[pattern[0]] = TopKPatternResult(size, i, pattern[1] / total_patterns, pattern[1])

all_patterns = list(map(lambda y: y[1], sorted(all_patterns.items(), key=lambda x: x[1].percentage, reverse=True)[:30]))

table = PrettyTable()
table.field_names = ["Size", "Pattern #", "Absolute Count", "Frequency of Size"]
for pattern in all_patterns:
    table.add_row([pattern.size, pattern.source_number, pattern.absolute_count, f"{pattern.percentage:.2%}"])
print(table)
