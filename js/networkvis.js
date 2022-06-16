class Networkvis {
    constructor(_data, _parentTag) {
        this.config = {
            width: 800,
            height: 500,
        }
        this.data = _data;
        this.parentTag = _parentTag;
        this.initVis();
    }
    initVis() {
        let vis = this;

        vis.hideIsolatedNodes = d3.select('#hideIsolatedNodes')
        .property('checked', false)
        .on('change', vis.checkboxUpdate);

        d3.select('#url_tagline')
        .html(`Visualising Repo: <a href=${vis.data.repo_url}>${vis.data.repo_url}</a>`)

        d3.select('#searchButton')
        .on('click', (d, e) => {
            let targetId = d3.select('#searchBox').node().value;
            let targetX = d3.select(`#point-${targetId}`).attr('x');
            let targetY = d3.select(`#point-${targetId}`).attr('y');

            let g = d3.select('#mainViewG')
            d3.zoom.translateTo(g, targetX, targetY);
        })
        let min_size_component = 1;
        let max_size_component = 1;
        for (let component of vis.data['connected_components']) {
            max_size_component = Math.max(component.length, max_size_component);
        }

    }

    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    nodeDragging(e, d) {
        d.fx = e.x;
        d.fy = e.y;
    }

    searchNode(id) {

    }

    renderTable(data) {
        data.connected_components = data.connected_components.filter(x => x.length > 1);
        data.connected_components.sort((a, b) => {
            return b.length - a.length;
        });
        let table = d3.select('#auxView').append('table')
        let thead = table.append('thead')
        let tbody = table.append('tbody')

        // Table header
        thead.append('tr')
        .selectAll('th')
        .data(['Family', 'Cardinality', 'Constituents Nodes'])
        .join('th')
        .text(d => d)

        let rows = tbody.selectAll('tr')
        .data(data.connected_components)
        .join('tr');

        let cells = rows.selectAll('td')
        .data((d, i) => {
            return [i, d.length, d];
        })
        .join('td')
        .text((d, i) => {return (i === 2 ? `{${d}}` : d)})
;
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

        vis.svg = d3.select(vis.parentTag)
        .insert('svg', '.sliderDiv + *')
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

        const node = vis.svg
        .append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(data.nodes)
        .join('g')
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
            let checked = d3.select('#rightClickHyperlink').property('checked')
            if (checked) {
                e.preventDefault();
                window.open(`${vis.data.repo_url}/pull/${d.id}`, '_blank').focus();
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
            .distance(50)
            .links(data.links))
        .force("collide", d3.forceCollide(5).radius(23))
        .force('charge', d3.forceManyBody().strength(-10))
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

        // vis.renderTable(data);
    }
    
}
