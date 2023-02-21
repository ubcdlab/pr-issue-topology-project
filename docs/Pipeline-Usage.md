# Pipeline Usage

The scripts located in `scripts/` and many of the other graph visualization scripts rely on graph information dumps in `data/`. These information dumps are named according to the repository they were sourced from.

There are two types of JSON files in `data/`: structures and graphs. Structures contain a basic mapping of connected component size to list of connected components in the dataset of that size. Graphs contain more detailed information on a node's (i.e. issue or PR) metadata, including its status (e.g. 'closed' or 'merged'), type, various timestamps, and comments and events. Each graph node also contains a list of all other nodes in its connected component. The 'id' of a node corresponds to the identifier of the node on GitHub. For example, a node with ID 950 in `graph_App-vNext-Polly.json` would correspond to the issue or pull request numbered 950 in `App-vNext/Polly`.

This data is generated via scripts found in `pipeline/`. There should not be any need to run additional scraping, but place a `.token` file in the root directory that holds a GitHub authentication token so the pipeline can fetch additional repository metadata if needed. 

There should not be any need to regenerate files in `data/` because all scraping has been completed. If you wish to do so, run `pipeline/stage_3.py`. If you only wish to generate one type, `BarChartCreator`'s `create_vis_for_all_repo` method will create structure JSON files, and `NetworkVisCreator` will create graph JSON files.

If you wish to use the raw scraped data (e.g. for generating the entire graph as a NetworkX Graph), use the `PickleReader` class in `pipeline/`. See `generate_all_patterns/generate_all_patterns_of_size.py` for example usage. The raw data is available as pickle files in `raw_data/`.

