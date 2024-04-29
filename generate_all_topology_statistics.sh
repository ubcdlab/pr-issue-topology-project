#!/bin/bash

python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/CompetingPRs.cypher --name=competition --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_1.cypher --name=consequence_1 --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_2.cypher --name=consequence_2 --to-csv
# python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/Consequence_3.cypher --name=consequence_3 --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/DecomposedIssue.cypher --name=decomposition --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/DuplicateIssueHub.cypher --name=duplicate --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/ExtendedPR.cypher --name=extended --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/DivergentPR.cypher --name=divergent --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/IntegratingPRHub.cypher --name=pr_hub --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/DependentPRs.cypher --name=dependent --to-csv
python -m data_scripts.topology_cc_occurrences --cypher=cypher_scripts/Same_Author.cypher --name=same_author --to-csv

python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/CompetingPRs.cypher --name=competition --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/Consequence_1.cypher --name=consequence_1 --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/Consequence_2.cypher --name=consequence_2 --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/DecomposedIssue.cypher --name=decomposition --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/DuplicateIssueHub.cypher --name=duplicate --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/ExtendedPR.cypher --name=extended --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/DivergentPR.cypher --name=divergent --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/IntegratingPRHub.cypher --name=pr_hub --to-csv
python -m data_scripts.neo4j_size_distributions --cypher=cypher_scripts/DependentPRs.cypher --name=dependent --to-csv


