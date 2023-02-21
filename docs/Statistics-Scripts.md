# Statistics Scripts

Several statistics scripts can be found in `scripts/`. These output total counts of certain types of nodes and calculate percentages of component characteristics.

Brief documentation for each command can be found below. Run each script like so: `python -m scripts.[script_name] [options]` as opposed to just running the bare Python script.

Many of the scripts read fields in structure JSON files in `data/` to fetch the list of nodes in a component, and use the graph JSON files in `data/` to fetch more specific information.

## Total Count

`python -m scripts.total_count`

Returns total number of components.

## Isolated Nodes Statistics

`python -m scripts.isolated_nodes_statistics --print=False`

Returns the percentage of issues and pull requests that are open / merged / closed. Also prints the total number of isolated components if `--print` is passed.

This command reads the `isolated` field from structure JSON files in `data/` to fetch all isolated nodes. It then reads the associated graph JSON file for the repository to fetch the type and status of the node.

## Diad Components Statistics

`python -m scripts.diad_components_statistics --closed=False`

Returns the distribution of connected components of size 2 (i.e. a single issue connected to a single PR and nothing else) across statuses. These statistics take direction of the connection into consideration. Each number is computed as a percentage of the total amount of size 2 components.

The `--closed` flag will also print additional information on the 'Closed Issue ↔ Merged PR' relationship. It separates the percentages by direction. The percentages are also calculated over the amount of all size 2 components.

This command fetches components of size 2 from the associated fields in structure JSON files in `data/`. Similarly to [the isolated nodes statistics script](#isolated-nodes-statistics), it then also reads from graph JSON files.

## Temporal Differences

`python -m scripts.temporal_differences --output_csv=[path] --small=False --print=False --save-all=False --repo-str="" --size=0`

Prints or writes information on the time delta between the earliest node creation and latest node update in connected components. Also computes average comment span duration for each connected component by taking the mean of the difference between node creation and last comment. Note that a node being marked as closed will not 'cut off' node updates, as in cases where a node is closed and reopened multiple times, and the script will take the final node update as its last update time regardless of the update type. When a node was not updated after its creation, deltas will show as 0.

The `--output_csv` flag specifies a location to export the CSV information to.

	By default, the script will only compute statistics for large components, or those with more than 100 nodes. The `--small` flag will compute statistics for small components, or those with 20 nodes or fewer. The `--size` flag will compute statistics only for components of a specific size. `--size` takes precedence over `--small`.

`--save-all` overrides all of these size settings, and will compute statistics for all components.

The `--print` flag is disabled by default, and when enabled will log output to standard out instead of to a file.

The `--repo-str` flag can be used to compute statistics only for components in a specific repository.

This script is used to test if there is a significant difference in the time deltas of large components as opposed to small components. A t-test of the two median deltas returned `p < 1.3 * 10^-9`.

