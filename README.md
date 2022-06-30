
# Yank Solicitation Project Crawler and Visualiser
## Dependencies
- [D3.js](https://d3js.org/), bundled within the `./js` directory as `d3.v6.min.js`
## Running and using the visualisation
From the root directory, host a local web server (`python3 -m http.server` usually does the trick), and then navigate to `localhost:8000` (assuming the server is hosted on port 8000).

From the dropdown menus that are shown, select the GitHub repositories that you wish to view. 
<img width="784" alt="image" src="https://user-images.githubusercontent.com/11191061/176245665-21b681f4-600e-4194-bbcd-5b559745560d.png">

The network visualisation for the repo will be loaded. The usual operations, such as scrolling the view up/down/left/right (trucking and booming), as well as zooming in and out, are supported.

<img width="628" alt="image" src="https://user-images.githubusercontent.com/11191061/176245756-b9a794c5-55ff-49e2-94da-333c06a49b41.png">

Currently, you can filter the visualised network graph to show only the desired connected component sizes. Drag the blue slider to restrict the range of connected component sizes to show. For example, if the endpoints of the slider shows `[10, 134]`, then only connected components of size between 10 nodes and 134 nodes *inclusive* will be shown.

You can also right click on a node within the network to open a link (in a new tab) directly to the issue/pull request the node represents. This behaviour can be disabled by unchecking the "right click to open node link" checkbox (usually for debugging purposes).

## Running the crawler
Work in progress
