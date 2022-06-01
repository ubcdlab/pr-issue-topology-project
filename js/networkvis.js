class Networkvis {
    constructor() {
        this.config = {
            width: 800,
            height: 800,
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
        .force('charge', d3.forceManyBody().strength(-1))
        .force('center', d3.forceCenter(vis.config.width / 2, vis.config.height / 2))
        .on("tick", ticked);

    }

    
}
