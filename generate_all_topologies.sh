#!/bin/bash

python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/CompetingPRs.cypher --name=competition
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_1.cypher --name=consequence_1
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_2.cypher --name=consequence_2
# python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_3.cypher --name=consequence_3
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/DecomposedIssue.cypher --name=decomposition
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/DuplicateIssueHub.cypher --name=duplicate
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/ExtendedPR.cypher --name=extended
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/DivergentPR.cypher --name=divergent
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/IntegratingPRHub.cypher --name=pr_hub
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/DependentPRs.cypher --name=dependent
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Same_Author.cypher --name=same_author

