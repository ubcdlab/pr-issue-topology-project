# Most Frequent Connected Components

`python -m generate_all_patterns.generate_all_patterns_of_size --size=5 --render=False --status --edge-direction`.

Finds all connected components of a given size, groups them into isomorphic classes ('patterns'), and finds the frequency of each pattern out of all patterns of that size. Reads from pickle files in `raw_data/`. By default, isomorphism depends only on node type (issue v.s. pull request) and edge type (e.g. 'fixes'). By default, edge direction and node status are not taken into consideration because this led to many variations of a semantically similar graph topology.

The `--size` flag indicates the specified component size.

The `--render` flag indicates whether or not to generate images in `images_dump/`.For more documentation on image generation, see [Generating Topology Images](./Generating-Topology-Images.md).

The `--status` flag indicates whether or not to take node status into consideration when computing if two graphs are isomorphic or not. By default, this is false.

Similarly, the `--edge-direction` flag indicates whether or not to take edge direction. By default, this is also false.

To generate all patterns (and all pattern images) of all sizes, run `./generate_all_images.sh`.

The script dumps the connected component to frequency mapping in `pattern_dump/`. If `--edge-direction` is set to false, it will save to `[size]_undirected.pk`; otherwise, it will save to `[size].pk`. `graph_[size].pk` files are a dump of a NetworkX graph of all connected components of a specific size across all repositories. `graph_[size]_undirected.pk` dump the NetworkX graphs in an undirected format.

If these script dump files exist, they will be read instead of re-computing all graphs and pattern frequencies. To override this, delete or rename the appropriate files in `pattern_dump/`.

The script uses multiprocessing with `cpu_count() / 2` cores to parallelize and speed up individual graph creation. Avoid repeatedly calling `g = nx.compose(g, g_2)` as this causes the entire graph to be copied at the end of each iteration. Instead, `g = nx.compose_all(graph_iterable)` is more efficient.

## All Pattern Statistics

`python -m generate_all_patterns.all_patterns_statistics --percentage-ordering=False --edge-direction=False --all=False`

Returns a list of the top 30 most frequent connected components across all component sizes along with their frequency and absolute count. The 'Size' and 'Pattern #' fields can be used to find an example of that connected component: `image_dump/[size]/[pattern #].png` will show an example of an isomorphic component.

Run `python -m generate_all_patterns.generate_all_patterns_of_size` first with the appropriate arguments (i.e. with `--edge-direction` if you wish to generate statistics with edge direction taken into consideration) to generate the pattern file dumps.

The `--percentage-ordering` flag will order not by absolute counts, but by the percentage of that component's size.

The `--edge-direction` flag will match edge directions in components as well. For example, a component with `I → PR` would not be considered isomorphic to `I ← PR`.

The `--all` flag will sort and return *all* the top 20 patterns for all sizes (as opposed to the top 30 of each size's top 20).

## Statistics on Patterns of `X` Size

`python -m generate_all_patterns.patterns_of_size_statistics --size=5 --write=False --edge-direction=False`

Returns a list of the top 20 most frequent connected components of a given size along with absolute counts and relative frequencies in order of most frequent. Reads from pickle files in `pattern_dump`.

The `--size` flag indicates the component size to return the top 20 of.

The `--write` flag will write output to the size's folder in `image_dump/`. For example, running with `size=5` and `--write` will write output to `image_dump/5/patterns.txt`.

See above for documentation on edge direction.

