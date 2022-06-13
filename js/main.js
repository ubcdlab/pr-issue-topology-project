
Promise.all([
  d3.json('data/graph.json'),
  d3.json('data/structure.json')
])
.then(data => {
  let graph_data = data[0];
  let structure_data = data[1];

  for (let node of graph_data.nodes) {
    node['isolated'] = true;
    for (let link of graph_data.links) {
      if (link.source === node.id || link.target === node.id) {
        node['isolated'] = false;
      }
    }
  }
  const networkplot = new Networkvis(graph_data, '#leftVis');
  networkplot.updateVis(graph_data);

  const patternplot = new Patternvis(structure_data, '#leftVis');
  patternplot.updateVis(structure_data);
})
.catch(error => {
  console.log(error);
})

// d3.json('data/graph.json').then(data => {
//   for (let node of data.nodes) {
//     node['isolated'] = true;
//     for (let link of data.links) {
//       if (link.source === node.id || link.target === node.id) {
//         node['isolated'] = false;
//       }
//     }
//   }
//   const networkplot = new Networkvis(data, '#leftVis');
//   networkplot.updateVis(data);
// })

// d3.json('data/structure.json').then(data => {
//   const patternplot = new Patternvis(data, '#leftVis');
//   patternplot.updateVis(data);
// })
// .catch(error => {
//   console.log(error);
// })

// d3.json('data/graph_thefuck.json').then(data => {
//   for (let node of data.nodes) {
//     node['isolated'] = true;
//     for (let link of data.links) {
//       if (link.source === node.id || link.target === node.id) {
//         node['isolated'] = false;
//       }
//     }
//   }
//   const networkplot = new Networkvis(data, '#q');
//   networkplot.updateVis(data);
// })

// d3.json('data/structure_thefuck.json').then(data => {
//   const patternplot = new Patternvis(data, '#frequency2');
//   patternplot.updateVis(data);
// })
// .catch(error => {
//   console.log(error);
// })

