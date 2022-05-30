


d3.json('data/vis_graph.json').then(data => {
  const networkplot = new Networkvis({});
  networkplot.updateVis(data);
})

