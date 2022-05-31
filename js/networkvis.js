class Networkvis {
    constructor() {
        this.config = {
            width: 1500,
            height: 1000,
        }
        this.data = null;
        this.initVis();
    }
    initVis() {
        let vis = this;
        vis.hideIsolatedNodes = d3.select('#hideIsolatedNodes')
        .on('change', vis.update);

    }
    update() {
        d3.selectAll('.isolated')
        .attr('opacity', d3.select('#hideIsolatedNodes').property('checked') ? 0.1 : 1)
    }

    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    drag_start(d, e) {
        let vis = this;
        //  if (!e.active)  {
        //     vis.simulation.alphaTarget(0.3).restart()
        // }
        d.fx = d.x;
        d.fy = d.y;
    }

    //make sure you can't drag the circle outside the box
    drag_drag(d, e) {
      d.fx = e.x;
      d.fy = e.y;
    }

    drag_end(d, e) {
        let vis = this;
    //   if (!e.active)  {
    //     vis.simulation.alphaTarget(0);
    // }
      d.fx = null;
      d.fy = null;
    }

    //Zoom functions 
    zoom_actions(e) {
        let vis = this;
        d3.select('#vis').attr("transform", e.transform)
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

        vis.svg = d3.select('#vis')
        .attr('width', vis.config.width)
        .attr('height', vis.config.height);

        let div = d3.select('body').append('div')   
        .attr('class', 'tooltip')               
        .style('opacity', 0);

        const links = vis.svg
        .selectAll('line')
        .data(data.links)
        .join('line')
        .style('stroke', '#aaa');

        const node = vis.svg
        .selectAll('circle')
        .data(data.nodes)
        .join('circle')
        .attr('class', 'circle')
        .classed('isolated', d => (d.isolated))
        .attr('r', 5)
        .style('fill', '#69b3a2')
        .on('mouseover', (event, d) => {
            div.transition()
                .duration(200)      
                .style('opacity', 1);      
            div.html(d.name)  
                .style('left', `${+event.pageX + 15}px`)     
                .style('top', `${+event.pageY}px`);    
            })
        .on('mouseout', d => {       
            div.transition()        
                .duration(500)      
                .style('opacity', 0);   
        })


        vis.simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink()
            .id(function(d) { return d.id; })
            .links(data.links))
        .force('charge', d3.forceManyBody().strength(-2))
        .force('center', d3.forceCenter(vis.config.width / 2, vis.config.height / 2))
        .on("tick", ticked );

        var drag_handler = d3.drag()
        .on("start", vis.drag_start)
        .on("drag", vis.drag_drag)
        .on("end", vis.drag_end);   
        
        drag_handler(node);

        //add zoom capabilities 
        var zoom_handler = d3.zoom()
            .on("zoom", vis.zoom_actions);

        zoom_handler(vis.svg); 
    }

    
}
