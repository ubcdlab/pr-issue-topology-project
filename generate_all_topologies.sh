#!/bin/bash

python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Competition.cypher --name=competition
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_1.cypher --name=consequence_1
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_2.cypher --name=consequence_2
# python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Consequence_3.cypher --name=consequence_3
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Decomposition.cypher --name=decomposition
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Duplicate_Hub.cypher --name=duplicate
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Improvement.cypher --name=improvement
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Optimization.cypher --name=optimization
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/PR_Hub.cypher --name=pr_hub
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/PR_Stack.cypher --name=pr_stack
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Release.cypher --name=release
python -m generate_neo4j_images.generate_from_neo4j --cypher=cypher_scripts/Same_Author.cypher --name=same_author

