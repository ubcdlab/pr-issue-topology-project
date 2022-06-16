
const LEFT_VIS_DIV_ID = '#leftVis'


Promise.all([
  d3.json('data/graph.json'),
  d3.json('data/structure.json')
])
.then(data => {
  let graph_data = data[0];
  let structure_data = data[1];

  const default_slider_value = [-Infinity, Infinity]
  let slider = d3.sliderBottom()
  .min(1)
  .max(computeLargestConnectedComponentSize(graph_data))
  .step(1)
  .displayValue(true)
  .width(400)
  .height(10)
  .ticks(10)
  .default(default_slider_value)
  .fill('skyblue')
  .on('end', (val) => {
      let modify = filterNetwork(val[0], val[1], graph_data)
      d3.select('#leftVis-view').remove();
      const networkplot2 = new Networkvis(modify, LEFT_VIS_DIV_ID);
      networkplot2.updateVis(modify);
  });

  d3.select(LEFT_VIS_DIV_ID)
  .append('svg')
  .attr('class', 'slider')
  .attr('width', '100%')
  .attr('height', 80)
  .append('g')
  .attr('transform', 'translate(30,30)')
  .call(slider);

  let modify = filterNetwork(-Infinity, Infinity, graph_data);
  const networkplot2 = new Networkvis(modify, LEFT_VIS_DIV_ID);
  networkplot2.updateVis(modify);

  const patternplot = new Patternvis(structure_data, LEFT_VIS_DIV_ID);
  patternplot.updateVis(structure_data);

})
.catch(error => {
  console.log(error);
})


function filterNetwork(min_size, max_size, data) {
  let modify = JSON.parse(JSON.stringify(data));
  let original_data = modify['nodes'];
  let links = modify['links'];
  let new_nodes = [];
  let new_links = new Set();

  for (let node of original_data) {
      if (min_size <= node['connected_component'].length && node['connected_component'].length <= max_size) {
          new_nodes.push(node);
          for (let link of links) {
              if (link['source'] === node.id || link['target'] === node.id) {
                  new_links.add(link);
              }
          }
      }
  }
  modify['nodes'] = new_nodes
  modify['links'] = Array.from(new_links);
  return modify;
}

function computeLargestConnectedComponentSize(data) {
  let max_size_component = 1;
  for (let component of data['connected_components']) {
      max_size_component = Math.max(component.length, max_size_component);
  }
  return max_size_component;
}