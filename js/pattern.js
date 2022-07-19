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

        let x_axis_keys = Object.entries(vis.data).filter((x, index) => {
            let result = {};
            let total_length = 0;
            for (let sub_entries of Object.values(x[1])) {
                total_length += sub_entries.length;
            }
            result[x[0]] = total_length;
            return total_length > 0;
        })
        
        x_axis_keys = x_axis_keys.map((x) => {
            return x[0];
        })
        
        vis.x = d3.scaleBand()
        .domain(x_axis_keys)
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
        let x_axis_entries = Object.entries(data).filter((element, index) => {
            if (element[1]['general']) {
                return element[1]['general'].length > 0;
            }
            return true;
        });
        console.log(data);
        let total_nodes_count = 0;
        for (let entry of Object.entries(data)) {
            for (let sub_entries of Object.values(entry[1])) {
                total_nodes_count += sub_entries.length * entry[0];
            }
        }
        console.log(total_nodes_count);

        let div = d3.select('body').append('div')   
        .attr('class', 'tooltip')               
        .style('opacity', 0);

        vis.svg.selectAll('.bar_rect')
        .data(x_axis_entries)
        .join('g')
        .attr('class', 'bar_rect_g')
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

        vis.svg.selectAll('.bar_rect_g')
        .append('text')
        .text((d) => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            return `${total_length} (${(total_length / total_nodes_count * 100).toFixed(1)}%)`;
        })
        .style('fill', 'black')
        .style('text-anchor', 'middle')
        .attr('x', (d) => vis.x(d[0]) + vis.x.bandwidth()/2)
        .attr('y', (d) => {
            let inner_object = d[1];
            let total_length = 0;
            for (let sub_entries of Object.values(inner_object)) {
                total_length += sub_entries.length;
            }
            return vis.y(total_length) - 5;
        })
    }
    
}
