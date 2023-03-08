#!/bin/bash

python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Competition.cypher --name=competition --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_1.cypher --name=consequence_1 --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_2.cypher --name=consequence_2 --to-csv
# python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_3.cypher --name=consequence_3 --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Decomposition.cypher --name=decomposition --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Duplicate_Hub.cypher --name=duplicate --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Improvement.cypher --name=improvement --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Optimization.cypher --name=optimization --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/PR_Hub.cypher --name=pr_hub --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/PR_Stack.cypher --name=pr_stack --to-csv
python -m scripts.topology_cc_occurrences --cypher=cypher_scripts/Same_Author.cypher --name=same_author --to-csv

