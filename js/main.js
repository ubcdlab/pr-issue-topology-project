

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
  // const networkplot = new Networkvis(graph_data, '#leftVis');
  // networkplot.updateVis(graph_data);

  // const patternplot = new Patternvis(structure_data, '#leftVis');
  // patternplot.updateVis(structure_data);

  let default_slider_value = [-Infinity, Infinity]
  let slider = d3.sliderBottom()
  .min(1)
  .max(100)
  .step(1)
  .displayValue(true)
  .width(400)
  .height(10)
  .ticks(10)
  .default(default_slider_value)
  .fill('skyblue')
  .on('onchange', (val) => {
      // console.log(val)
      let min_size = val[0];
      let max_size = val[1];
      let modify = JSON.parse(JSON.stringify(data[0]));
      let original_data = modify['nodes'];
      let links = modify['links'];
      let new_nodes = [];
      let new_links = new Set();

      for (let node of original_data) {
          if (min_size <= node['connected_component'].length && node['connected_component'].length <= max_size) {
              new_nodes.push(node);
              for (let link of links) {
                  if (link['source'].id === node.id || link['target'].id === node.id) {
                      new_links.add(link);
                  }
              }
          }
      }
      modify['nodes'] = new_nodes
      modify['links'] = Array.from(new_links);
      // console.log(modify)
      d3.select('#leftVis-view').remove();
      const networkplot2 = new Networkvis(modify, '#leftVis');
      networkplot2.updateVis(modify);
  });

  d3.select('#rightVis')
  .append('svg')
  .attr('class', 'slider')
  .attr('width', '100%')
  .attr('height', 80)
  .append('g')
  .attr('transform', 'translate(30,30)')
  .call(slider);

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

