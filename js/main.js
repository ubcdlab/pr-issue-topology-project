

this.createVisInstance('#leftVis', 'data/graph_jekyll-admin.json', 'data/structure_jekyll-admin.json');
this.createVisInstance('#rightVis', 'data/graph_Notepads.json', 'data/structure_Notepads.json');

function createVisInstance(DIV_ID, graph_json_file, structure_json_file) {
    Promise.all([
    d3.json(graph_json_file),
    d3.json(structure_json_file)
  ])
  .then(data => {
    let graph_data = data[0];
    let structure_data = data[1];

    console.log(graph_data);

    const default_slider_value = [-Infinity, Infinity]

    let statsDiv = d3.select(DIV_ID)
    .append('div')
    .attr('id', `${DIV_ID.substring(1)}_statsDiv`)
    .style('width', '100%')
    .style('height', '50px');

    this.initStatsPanel(statsDiv, graph_data);

    let sliderDiv = d3.select(DIV_ID)
    .append('svg')
    .attr('id', `${DIV_ID.substring(1)}_sliderDiv`)
    .style('width', '100%')
    .style('height', '80px');

    let slider = d3.sliderBottom()
    .min(2)
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
        d3.select(`${DIV_ID}-view`).remove();
        const networkplot2 = new Networkvis(modify, DIV_ID);
        networkplot2.updateVis(modify);
        computeStatistics(statsDiv, graph_data, modify)
    });

    d3.select(`${DIV_ID}_sliderDiv`)
    .append('svg')
    .attr('class', 'slider')
    .attr('id', `${DIV_ID}-slider-div`)
    .attr('width', '100%')
    .attr('height', 80)
    .append('g')
    .attr('transform', 'translate(30,30)')
    .call(slider);

    let modify = filterNetwork(-Infinity, Infinity, graph_data);
    const networkplot2 = new Networkvis(modify, DIV_ID);
    networkplot2.updateVis(modify);

    computeStatistics(statsDiv, graph_data, modify);
    
    const patternplot = new Patternvis(structure_data, DIV_ID);
    patternplot.updateVis(structure_data);

  })
  .catch(error => {
    console.log(error);
  })
}


function initStatsPanel(statsDiv, data) {
  statsDiv
  .html(`
Repo URL: <a href="${data.repo_url}">${data.repo_url}</a><br>
Visualising <span id="filtered_quantity">n</span> nodes (<span id="unfiltered_quantity">x</span> total) in <span>n</span> components
              <br>
              <span id="issues_quantity">x</span> issues (<span id="issues_quantity_percent">x%</span>): 

              <span id="closed_issue">y</span><span style="color: rgb(218, 54, 51);"> closed </span> (<span id="closed_issue_percent">x%</span>); 
              <span id="open_issue">z</span><span style="color: rgb(35, 134, 54)"> open </span>(<span id="open_issue_percent">x%</span>)

              <br>
              <span id="pull_request_quantity">x</span> pull requests (<span id="pull_request_percent">x%</span>): 

              <span id="closed_pull_request">y</span> <span style="color: rgb(218, 54, 51);"> closed </span> (<span id="closed_pull_request_percent">x%</span>); 
              <span id="open_pull_request">z</span> <span style="color: rgb(35, 134, 54)"> open </span> (<span id="open_pull_request_percent">x%</span>);
              <span id="merged_pull_request">z</span> <span style="color: rgb(137, 87, 229)"> merged </span> (<span id="merged_pull_request_percent">x%</span>);
`)

}


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

function computeStatistics(parentDiv, data, filtered) {
  console.log(filtered.nodes);

  let total_node_quantity = data.nodes.length;
  let filtered_node_quantity = filtered.nodes.length;
  let issues_quantity = 0;
  let closed_issues = 0;
  let open_issues = 0;

  let pull_request_quantity = 0; 
  let open_pull_request = 0;
  let closed_pull_request = 0;
  let merged_pull_request = 0;

  for (let node of filtered.nodes) {
    if (node.type === 'issue') {
      issues_quantity += 1;
      if (node.status === 'closed') {
        closed_issues += 1;
      } else {
        open_issues += 1;
      }
    } else {
      pull_request_quantity += 1;
      if (node.status === 'closed') {
        closed_pull_request += 1;
      } else if (node.status === 'open') {
        open_pull_request += 1;
      } else {
        merged_pull_request += 1;
      }
    }
  }

  // we can do this more elegently in an object, a note for
  // future self

  parentDiv.select('#unfiltered_quantity').text(total_node_quantity);
  parentDiv.select('#filtered_quantity').text(filtered_node_quantity);

  parentDiv.select('#issues_quantity').text(issues_quantity);
  parentDiv.select('#pull_request_quantity').text(pull_request_quantity);

  parentDiv.select('#issues_quantity_percent').text(`${(issues_quantity/filtered_node_quantity * 100).toFixed(1)}%`);
  parentDiv.select('#pull_request_percent').text(`${(pull_request_quantity/filtered_node_quantity * 100).toFixed(1)}%`);

  parentDiv.select('#closed_issue').text(closed_issues);
  parentDiv.select('#closed_issue_percent').text(`${(closed_issues/issues_quantity * 100).toFixed(1)}%`)
  parentDiv.select('#open_issue').text(open_issues)
  parentDiv.select('#open_issue_percent').text(`${(open_issues/issues_quantity * 100).toFixed(1)}%`)

  parentDiv.select('#closed_pull_request').text(closed_pull_request)
  parentDiv.select('#closed_pull_request_percent').text(`${(closed_pull_request/pull_request_quantity * 100).toFixed(1)}%`)
  parentDiv.select('#open_pull_request').text(open_pull_request)
  parentDiv.select('#open_pull_request_percent').text(`${(open_pull_request/pull_request_quantity * 100).toFixed(1)}%`)
  parentDiv.select('#merged_pull_request').text(merged_pull_request)
  parentDiv.select('#merged_pull_request_percent').text(`${(merged_pull_request/pull_request_quantity * 100).toFixed(1)}%`)
}