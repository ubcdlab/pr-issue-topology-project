# Revealing Work Practices in Pull-Based Software Development through Issue-PR Graph Topologies

Scripts and data for quantitative analysis in the above paper and associated CPSC448 Directed Studies work. The goal of this work is to enable topological analysis of PR-Issue networks on GitHub via graph database queries, an image generation module, and many statistics scripts.

The raw data scraped from GitHub, including the issues, the PRs, their links, and their comment data, is available as Pickle files, downloadable [here](https://osf.io/29aev/). The OSF dataset also includes the Neo4J database dump as well as all generated workflow type instance images.

For documentation, see [the `docs/` folder](./docs/).

- To get started with the graph database data, see [this documentation](./docs/Neo4J.md).
- To learn more about the image generation module, see [this documentation](./docs/Generating-Topology-Images.md).
- The full database dump is available [here](https://osf.io/3kexy). To import the database in your Neo4J instance, follow the [Neo4J documentation here](https://neo4j.com/docs/aura/auradb/importing/import-database/).
- The Cypher queries are [here](./cypher_scripts/). To run the queries and return the issues and PRs that are part of each workflow type, drag and drop the query over the query GUI.
- The scripts for component sampling are [here](./archive/pipeline/) and additional documentation is [here](https://docs.google.com/document/d/1MWDp3d1xirGBRDDQPGLe2bq1639bEWLQTMzbUCWDdOo/view#heading=h.9q8lgk5wlfct).
