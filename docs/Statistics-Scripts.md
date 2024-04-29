# Statistics Scripts

Several statistics scripts can be found in `data_scripts/`. These output total counts of certain types of nodes and calculate percentages of component characteristics.

Brief documentation for each command can be found below. Run each script like so: `python -m data_scripts.[script_name] [options]` as opposed to just running the bare Python script.

Many of the scripts read fields in structure JSON files in `data/` to fetch the list of nodes in a component, and use the graph JSON files in `data/` to fetch more specific information.

## Total Count

`python -m data_scripts.total_count`

Returns total number of components.

## Isolated Nodes Statistics

`python -m data_scripts.isolated_nodes_statistics --print=False`

Returns the percentage of issues and pull requests that are open / merged / closed. Also prints the total number of isolated components if `--print` is passed.

This command reads the `isolated` field from structure JSON files in `data/` to fetch all isolated nodes. It then reads the associated graph JSON file for the repository to fetch the type and status of the node.

## Diad Components Statistics

`python -m data_scripts.diad_components_statistics --closed=False`

Returns the distribution of connected components of size 2 (i.e. a single issue connected to a single PR and nothing else) across statuses. These statistics take direction of the connection into consideration. Each number is computed as a percentage of the total amount of size 2 components.

The `--closed` flag will also print additional information on the 'Closed Issue ↔ Merged PR' relationship. It separates the percentages by direction. The percentages are also calculated over the amount of all size 2 components.

This command fetches components of size 2 from the associated fields in structure JSON files in `data/`. Similarly to [the isolated nodes statistics script](#isolated-nodes-statistics), it then also reads from graph JSON files.

## Temporal Differences

`python -m data_scripts.temporal_differences --output_csv=[path] --small=False --print=False --save-all=False --repo-str="" --size=0`

Prints or writes information on the time delta between the earliest node creation and latest node update in connected components. Also computes average comment span duration for each connected component by taking the mean of the difference between node creation and last comment. Note that a node being marked as closed will not 'cut off' node updates, as in cases where a node is closed and reopened multiple times, and the script will take the final node update as its last update time regardless of the update type. When a node was not updated after its creation, deltas will show as 0.

The `--output_csv` flag specifies a location to export the CSV information to.

    By default, the script will only compute statistics for large components, or those with more than 100 nodes. The `--small` flag will compute statistics for small components, or those with 10 nodes or fewer. The `--size` flag will compute statistics only for components of a specific size. `--size` takes precedence over `--small`.

`--save-all` overrides all of these size settings, and will compute statistics for all components.

The `--print` flag is disabled by default, and when enabled will log output to standard out instead of to a file.

The `--repo-str` flag can be used to compute statistics only for components in a specific repository.

This script is used to test if there is a significant difference in the time deltas of large components as opposed to small components. A t-test of the two median deltas returned `p < 1.3 * 10^-9`.

## Neo4J Query Match Size Distributions

`python -m data_scripts.neo4j_size_distributions --cypher=[cypher_path] --name=[pattern_name] --to-csv=False`

Reads the Cypher query supplied and executes it on a local Neo4J database. Prints a table of statistics mapping the size of a match to its frequency. This is useful for calculating statistics on how many 'spoke' nodes are in matches for topologies with node multiplicity or a star topology (i.e. competition, with its `n` PRs connected to a single issue).

The `--to-csv` parameter will redirect output to a CSV file located in `neo4j_statistics/size_distribution/` named by the `--name` parameter.

## Repo Component Statistics

`python -m data_scripts.repo_component_statistics --print-repos=False`

Computes the number of connected components in the graph of each repository, and prints summary statistics for their distribution.

The `--print-repos` flag will print an additional table mapping each repository to the number of connected components in it, sorted in decreasing order by number of components.

## Topology Occurrences in Connected Component Statistics

`python -m data_scripts.topology_cc_occurrences --cypher=[cypher_path] --name=[file_name] --to-csv=False`

Computes match topology connected component opportunities for connected components of each size across all repositories. Prints statistics summaries for each connected component size, ordered by number of matches of the topology in connected components of that size.

MTCO (matched topology component opportunities) describes the number of times the topology could have occurred within a component but did not, over the total number of nodes in the topology. This metric represents how likely a topology occurred by chance in the component, with higher MTCOs indicating that it’s more unlikely a match occurred by chance. MTCOs of 0 indicate that there were no other opportunities of the topology occurring within the component (if all nodes were of a different node type or status, for example), and higher MTCOs represent more potential for a match to have occurred.

Queries passed into this script are expected to have a `proportion` result returned. This result should be match-specific, and should be `# of nodes of same type and same status as a 'main' node in the topology in component / # nodes in component`. See `cypher_scripts/` for examples of how this is computed. This requires calling the query twice: first to collect all possible IDs, then again to search for nodes in a match's connected component and finding 'missed opportunities'.

The `--to-csv` flag saves the results into a CSV file named by `--name` in `neo4j_statistics/`. instead of printing them.

Regenerate statistics in `neo4j_statistics` for all topologies with `./generate_all_topologies.sh`

The script `data_scripts/topology_repo_occurrences` computes the same statistics, but groups results based on matches within the same repository instead of the same component size across all repositories.
