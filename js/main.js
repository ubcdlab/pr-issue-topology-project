


d3.json('data/vis_graph.json').then(data => {
  console.log(data);
  const networkplot = new Networkvis({});
  networkplot.updateVis(data);
})

