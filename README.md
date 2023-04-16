# Revealing Work Practices in Pull-Based Software Development through Issue-PR Graph Topologies

Scripts and data for quantitative analysis in the above paper and associated CPSC448 Directed Studies work.

The goal of this work is to enable topological analysis of PR-Issue networks on GitHub via graph database queries, an image generation module, and many statistics scripts.

For documentation, see [the `docs/` folder](./docs/).

- To get started with the graph database data, see [this file](./docs/Neo4J.md).
- To learn more about the image generation module, see [this file](./docs/Generating-Topology-Images.md).
- The full database dump is available [here](./neo4j.dump)
- The Cypher queries are [here](./cypher_scripts/).

My (Emilie's) CPSC448 paper is available [here](#TODO).

- RQ1 corresponds to work in [`cypher_scripts`](./cypher_scripts), [`generate_neo4j_images`](./generate_neo4j_images), and [these](./scripts/repo_topology_frequencies.py) [scripts](./scripts/neo4j_size_distributions.py).
- RQ2 corresponds to work in [these](./scripts/repo_topology_match.py) [three](./scripts/biggest_repos.py) [scripts](./scripts/most_common_repo_matches.py).
- RQ3 corresponds to work in [this script](./scripts/repo_topology_match.py).
- RQ4 corresponds to work in these scripts: [this](./scripts/issue_pr_cc_size_distribution.py), [this](./scripts/issue_status_cc_size_distribution.py), [this](./scripts/pr_status_cc_size_distribution.py), and [this](./scripts/cc_time_duration_image.py).
- RQ5 corresponds to work in [`image_dump`](./image_dump) and [`generate_all_patterns`](./generate_all_patterns).
