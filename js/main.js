


d3.json('data/graph.json').then(data => {
  for (let node of data.nodes) {
    node['isolated'] = true;
    for (let link of data.links) {
      if (link.source === node.id || link.target === node.id) {
        node['isolated'] = false;
      }
    }
  }
  const networkplot = new Networkvis(data, '#q');
  networkplot.updateVis(data);
})
.catch(error => {
  console.log(error);
})

d3.json('data/structure.json').then(data => {
  console.log(data);
  const patternplot = new Patternvis(data, '#frequency');
  patternplot.updateVis(data);
})
.catch(error => {
  console.log(error);
})

d3.json('data/graph_thefuck.json').then(data => {
  for (let node of data.nodes) {
    node['isolated'] = true;
    for (let link of data.links) {
      if (link.source === node.id || link.target === node.id) {
        node['isolated'] = false;
      }
    }
  }
  const networkplot = new Networkvis(data, '#q');
  networkplot.updateVis(data);
})

