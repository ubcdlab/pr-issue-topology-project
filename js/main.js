


d3.json('data/graph.json').then(data => {
  for (let node of data.nodes) {
    node['isolated'] = true;
    for (let link of data.links) {
      if (link.source === node.id || link.target === node.id) {
        node['isolated'] = false;
      }
    }
  }
  // console.log(data);

  const networkplot = new Networkvis(data);
  networkplot.updateVis(data);

  const patternplot = new Patternvis({});
  patternplot.updateVis({});
})
.catch(error => {
  console.log(error);
})

