class Networkvis {
    constructor(_data) {
        this.config = {
            width: 800,
            height: 500,
        }
        this.data = _data;
        this.initVis();
    }
    initVis() {
        let vis = this;
        vis.hideIsolatedNodes = d3.select('#hideIsolatedNodes')
        .property('checked', false)
        .on('change', vis.checkboxUpdate);

        d3.select('#url_tagline')
        .html(`Visualising Repo URL: <a href=${vis.data.repo_url}>${vis.data.repo_url}</a>`)
    }
    checkboxUpdate() {
        d3.selectAll('.isolated')
        .attr('opacity', d3.select('#hideIsolatedNodes').property('checked') ? 0.1 : 1)
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

            circle
                 .attr("x", function (d) { return d.x; })
                 .attr("y", function(d) { return d.y; });
        }

        let vis = this;

        vis.svg = d3.select('#vis')
        .attr('width', vis.config.width)
        .attr('height', vis.config.height)
        .call(d3.zoom().on('zoom', function (e) {
            vis.svg.attr('transform', e.transform)
        }))
        .append('g');

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
        .selectAll('rect')
        .data(data.nodes)

        const circle = node
        .join('rect')
        .attr('class', 'rect')
        .classed('isolated', d => (d.isolated))
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
        .on('mouseover', (event, d) => {
            // show the tooltip
            div.transition()
                .duration(200)      
                .style('opacity', 1);      
            div.html(`Node Number: ${d.id}<br>
Type: ${d.type}<br>
Status: ${d.status}<br>
Degree: ${d.node_degree}<br>
Component: ${d.connected_component}<br>
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
        .on('mouseout', d => {       
            div.transition()        
                .duration(500)      
                .style('opacity', 0);
            d3.selectAll('.highlighted')
            .classed('highlighted', false);   
        })
        .on('contextmenu', (e, d) => {
            // e.preventDefault();
            // window.open(`${vis.data.repo_url}/pull/${d.id}`, '_blank').focus();
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

        circle.append('text')
        .text('text')
        .attr('dy', d => d.y)


        var simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink()
            .id(function(d) { return d.id; })
            .distance(100)
            .links(data.links))
        .force("collide", d3.forceCollide(20).radius(20))
        .force('charge', d3.forceManyBody().strength(-15))
        .force('center', d3.forceCenter(vis.config.width / 2, vis.config.height / 2))
        .on("tick", ticked);

    }

    
}
