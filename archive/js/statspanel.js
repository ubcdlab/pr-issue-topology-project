class Patternvis {
    constructor(_data, _svgTag) {
        this.config = {
            width: 530,
            height: 300,
            margin: 40
        }
        this.data = _data;
        this.svgTag = _svgTag;
        this.initVis();
    }
    initVis() {
        let vis = this;
        let total_nodes = 0;
        for (let sub_entries of Object.values(vis.data)) {
            for (let final_entries of Object.values(sub_entries)){
                total_nodes = Math.max(final_entries.length, total_nodes);
            }
        }
        
        vis.svg = d3.select(vis.svgTag)
        .append('svg')
        .attr('width', '100%')
        .attr('height', vis.config.height)
        .append('g')
        .attr('class', 'patternVisArea')
        .attr('transform', `translate(${vis.config.margin}, ${vis.config.margin - 20})`)

        vis.x = d3.scaleBand()
        .domain(Object.keys(vis.data))
        .range([0, vis.config.width])
        .padding(0.2)

        vis.y = d3.scaleLinear()
        .range([vis.config.height - vis.config.margin, 0])
        .domain([0, total_nodes])

        vis.svg.append('g')
        .attr('class', 'yAxis')
        .call(d3.axisLeft(vis.y));
        vis.svg.append('g')
        .attr('class', 'xAxis')
        .call(d3.axisBottom(vis.x).tickValues(Object.keys(vis.data).filter((element, index) => {
            return Object.values(vis.data[element])[0].length > 0;
        })))
        .attr('transform', `translate(0, ${vis.config.height - vis.config.margin})`)
    }
    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    renderVis(data) {
        let vis = this;

        let div = d3.select('body').append('div')   
        .attr('class', 'tooltip')               
        .style('opacity', 0);

        vis.svg.selectAll('.bar_rect')
        .data(Object.entries(data))
        .join('g')
        .append('rect')
        .attr('class', 'bar_rect')
        .attr('id', (d) => `bar_${d[0]}`)
        .attr('x', (d) => vis.x(d[0]))
        .attr('y', (d) => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            return vis.y(total_length);
        })
        .attr('height', d => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            return vis.y(0) - vis.y(total_length);
        })
        .attr('width', vis.x.bandwidth())
        .on('mouseover', (event, d) => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            div.transition()
                .duration(200)      
                .style('opacity', 1);      
            div.html(`Component Size: ${d[0]}<br>Frequency: ${total_length}`)
            .style('left', `${+event.pageX + 15}px`)     
            .style('top', `${+event.pageY}px`);  
        })
        .on('mouseout', (e, d) => {
            div.transition()        
                .duration(500)      
                .style('opacity', 0);
        })
        .on('click', (e, d) => {
            d3.select(`#bar_${d[0]}`)
            .classed('highlighted_bar', !d3.select(`#bar_${d[0]}`).classed('highlighted_bar'))
        })

        let filtered = Object.entries(data).filter((element, index) => {
            return Object.values(element[1])[0].length > 0;
        });
        vis.svg.selectAll('.bar_rect_mouseover')
        .data(Object.entries(data))
        .join('g')
        .append('rect')
        .attr('class', 'bar_rect_mouseover')
        .attr('id', (d) => `bar_mouseover_${d[0]}`)
        .attr('x', (d) => vis.x(d[0]))
        .attr('y', (d) => 0)
        .attr('height', d => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            return vis.y(total_length);
        })
        .attr('width', vis.x.bandwidth())
        .style('opacity', 0)
        .attr('fill', 'transparent')
        .style('stroke', '#FFBF00')
        .style('stroke-width', 2)
        .on('mouseover', (event, d) => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            if (total_length >= 1) {
                d3.select(`#bar_mouseover_${d[0]}`).style('opacity', 1)
                div.transition()
                .duration(200)      
                .style('opacity', 1);      
                div.html(`Component Size: ${d[0]}<br>Frequency: ${total_length}`)
                .style('left', `${+event.pageX + 15}px`)     
                .style('top', `${+event.pageY}px`);  
            }
        })
        .on('mouseout', (e, d) => {
            div.transition()        
                .duration(500)      
                .style('opacity', 0);
            d3.select(`#bar_mouseover_${d[0]}`).style('opacity', 0)
        })
        .on('click', (e, d) => {
            d3.select(`#bar_${d[0]}`)
            .classed('highlighted_bar', !d3.select(`#bar_${d[0]}`).classed('highlighted_bar'))
        })
    }
    
}
