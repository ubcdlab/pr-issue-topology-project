class Networkvis {
    constructor(_data, _parentTag) {
        this.config = {
            width: 800,
            height: 500,
        }
        this.data = _data;
        this.parentTag = _parentTag;
        this.filterNet = {}
        this.initVis();
    }

    initVis() {
        let vis = this;

        d3.select(`${vis.parentTag}`)
        .select('.showNodeLabels')
        .on('change', (e) => {
            let val = d3.select(vis.parentTag).select('.showNodeLabels').property('checked');
            d3.selectAll('.number_label')
            .style('opacity', +val)
        })

        d3.select('#url_tagline')
        .html(`Visualising Repo: <a href=${vis.data.repo_url}>${vis.data.repo_url}</a>`)
    }

    updateFilter(criteria) {
        let vis = this;
        if (criteria === null) {
            vis.filterNet = {}
        } else {
            for (let [key, data] of Object.entries(criteria)) {
                vis.filterNet[key] = data
            }
        }
        console.log(vis.filterNet);
        let modify = vis.filterData();
        vis.updateVis(modify);
    }

    filterData(data) {
        let vis = this;
        let modify = structuredClone(vis.data);
        let original_data = modify['nodes'];
        let links = modify['links'];
        let new_nodes = [];
        let new_links = new Set();

        for (let node of original_data) {
            let keep = true;
            for (let [key, data] of Object.entries(vis.filterNet)) {
                if (data.length > 0) {
                    if (node[key].length === 0 && data.length > 0) {
                        keep = false;
                    } else if (!node[key].some(x => data.includes(x))) {
                        keep = false;
                        continue
                    }
                }
            }
            if (keep) {
                new_nodes.push(node);
            }
        }
        for (let link of links) {
            if (new_nodes.includes(link['source']) && new_nodes.includes(link['target'])) {
                new_links.add(link);
          }
        }
        modify['nodes'] = new_nodes
        modify['links'] = Array.from(new_links);
        console.log(modify);
        return modify;
    }

    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    nodeDragging(e, d) {
        d.fx = e.x;
        d.fy = e.y;
    }


    renderVis(data) {
        function ticked() {
            links
                .attr("x1", function(d) { return d.source.x+8; })
                .attr("y1", function(d) { return d.source.y+8; })
                .attr("x2", function(d) { return d.target.x+8; })
                .attr("y2", function(d) { return d.target.y+8; });

                node.attr('transform', d => {
                    return `translate(${d.x}, ${d.y})`
                })
        }

        let vis = this;

        d3.select(`${vis.parentTag}-view`).remove();

        vis.svg = d3.select(vis.parentTag)
        .insert('svg', `${vis.parentTag}_sliderDiv + *`)
        .attr('id', `${vis.parentTag.substring(1)}-view`)
        .classed('view', true)
        .attr('width', '100%')
        .attr('height', vis.config.height)
        .call(d3.zoom().on('zoom', function (e) {
            vis.svg.attr('transform', e.transform)
        }))
        .append('g')
        .attr('id', 'mainViewG');

        let div = d3.select('body').append('div')   
        .attr('class', 'tooltip')               
        .style('opacity', 0);

        const links = vis.svg
        .selectAll('line')
        .data(data.links)
        .join('line')
        .style('stroke', '#000')
        .attr('stroke-width', 2)
        .attr('marker-end', 'url(#triangle)')
        .attr('id', d => `link-${d.source}-${d.target}-end`)
        .on('click', (e, d) => {
            if (!d.colourIndex) {
                d.colourIndex = 0;
            }
            // https://colorbrewer2.org
            const colours = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf', '#000000']
            d3.select(`#link-${d.source.id}-${d.target.id}-end`)
            .style('stroke', colours[d.colourIndex++ % colours.length]);
        })
        .on('mouseover', (e, d) => {
            d3.select(`#link-${d.source.id}-${d.target.id}-end`)
            .classed('highlighted', true)
        })
        .on('mouseout', (e, d) => {
            d3.select(`#link-${d.source.id}-${d.target.id}-end`)
            .classed('highlighted', false)
        })

        const node = vis.svg
        .append('g')
        .selectAll('g')
        .data(data.nodes)
        .join('g')
        .attr('class', 'nodes')
        .classed('issues', d => {
            return d.type === 'issue' ? true : false;
        })
        .classed('pull_request', d => {
            return d.type === 'pull_request' ? true : false;
        })
        .on('mouseover', (event, d) => {
            // show the tooltip
            div.transition()
                .duration(200)      
                .style('opacity', 1);      
            div.html(`Node Number: ${d.id}<br>
Type: ${d.type}<br>
Status: ${d.status}<br>
Degree: ${d.node_degree}<br>
Component: ${d.connected_component.toString().replace(/(.{50})..+/, "$1...")}<br>
Component Size: ${d.connected_component.length}`)  
                .style('left', `${+event.pageX + 15}px`)     
                .style('top', `${+event.pageY}px`);
            // highlight the connected component
            for (let id of d.connected_component) {
                d3.select(`#point-${id}`)
                .classed('highlighted', true);
                let selector = document.querySelector(`[id^="link-${id}"`);
                d3.selectAll(`[id^="link-${id}-"`)
                .classed('highlighted', true);
            }
        })
        .on('mouseout', (e, d) => {    
            div.transition()        
                .duration(500)      
                .style('opacity', 0);
            d3.selectAll('.highlighted')
            .classed('highlighted', false);   
        })
        .on('contextmenu', (e, d) => {
            e.preventDefault();
            if (e.ctrlKey) {
                // console.log('whoa')
            } else {
                let checked = d3.select(vis.parentTag).select('.rightClickHyperlink').property('checked')
                if (checked) {
                    window.open(`${vis.data.repo_url}/pull/${d.id}`, '_blank').focus();
                }
            }
        })
        .call(d3.drag()
            .on('start', (d, e) => {
                if (!e.active) {
                    simulation.alphaTarget(0.3).restart();
                }
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', vis.nodeDragging)
            .on('end', (d, e) => {
                if (!e.active) {
                    simulation.alphaTarget(0);
                }
                d.fx = null;
                d.fy = null;
            }))

        const circle = node
        .append('rect')
        .attr('class', 'rect')
        .attr('id', d => `point-${d.id}`)
        .attr('number', d => d.id)
        .attr('width', 16)
        .attr('height', 16)
        .attr('rx', d => d.type === 'pull_request' ? 9999 : 0)
        .attr('ry', d => d.type === 'pull_request' ? 9999 : 0)
        .style('fill', d => {
            switch (d.status) {
                case 'closed':
                    return '#da3633'
                case 'open':
                    return '#238636'
                case 'merged':
                    return '#8957e5' 
            }
        })

        var simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink()
            .id(function(d) { return d.id; })
            .distance(80)
            .links(data.links))
        .force("collide", d3.forceCollide(5).radius(23))
        .force('charge', d3.forceManyBody().strength(-20))
        .force('center', d3.forceCenter(vis.config.width / 2, vis.config.height / 2))
        .on("tick", ticked);

        vis.svg.selectAll('.issues')
        .append('text')
        .text('i')
        .style('fill', 'white')
        .attr('x', 6)
        .attr('y', 14);

        vis.svg.selectAll('.pull_request')
        .append('text')
        .text('p')
        .style('fill', 'white')
        .attr('x', 5)
        .attr('y', 12);

        vis.svg.selectAll('.nodes')
        .append('text')
        .classed('number_label', true)
        .text((d) => d.id);
    }
    
}
