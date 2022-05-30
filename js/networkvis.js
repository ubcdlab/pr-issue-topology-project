class Networkvis {
    constructor() {
        this.config = {
            width: 900,
            height: 900,
        }
        this.initVis();
    }
    initVis() {
        let vis = this;
        vis.svg = d3.select('#vis')
        .append('svg')
        .attr('width', vis.config.width)
        .attr('height', vis.config.height);
    }
    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }
    renderVis(data) {
        function ticked() {
            links
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node
                 .attr("cx", function (d) { return d.x; })
                 .attr("cy", function(d) { return d.y; });
          }
        let vis = this;
        const links = vis.svg
        .selectAll('line')
        .data(data.links)
        .join('line')
        .style('stroke', '#aaa');

        const node = vis.svg
        .selectAll('circle')
        .data(data.nodes)
        .join('circle')
        .attr('r', 5)
        .style('fill', '#69b3a2')

        const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink()
            .id(function(d) { return d.id; })
            .links(data.links))
        .force('charge', d3.forceManyBody().strength(-1))
        .force('center', d3.forceCenter(vis.config.width / 2, vis.config.height / 2))
        .on('end', ticked);

    }
    
}
