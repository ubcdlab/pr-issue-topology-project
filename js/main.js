


d3.json('data/vis_graph.json').then(data => {
  for (let node of data.nodes) {
    node['isolated'] = true;
    for (let link of data.links) {
      // console.log(link)
      if (link.source === node.id || link.target === node.id) {
        node['isolated'] = false;
      }
    }
  }
  // console.log(data);

  const networkplot = new Networkvis(data);
  networkplot.updateVis(data);
})
.catch(error => {
  console.log(error);
})

