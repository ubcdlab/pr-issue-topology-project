class Patternvis {
    constructor(_data, _svgTag) {
        this.config = {
            width: 530,
            height: 400,
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
                total_nodes += final_entries.length;
            }
        }
        
        vis.svg = d3.select(vis.svgTag)
        .attr('width', '100%')
        .attr('height', vis.config.height)
        .append('g')
        .attr('class', 'patternVisArea')
        .attr('transform', `translate(${vis.config.margin}, ${vis.config.margin - 20})`)

        vis.x = d3.scaleBand()
        .domain(Object.keys(vis.data))
        .range([0, vis.config.width])

        vis.y = d3.scaleLinear()
        .range([vis.config.height - vis.config.margin, 0])
        .domain([0, total_nodes])

        vis.svg.append('g')
        .attr('class', 'yAxis')
        .call(d3.axisLeft(vis.y));
        vis.svg.append('g')
        .attr('class', 'xAxis')
        .call(d3.axisBottom(vis.x).tickValues(Object.keys(vis.data).filter((element, index) => { return index % 5 === 0;})))
        .attr('transform', `translate(0, ${vis.config.height - vis.config.margin})`)
    }
    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    renderVis(data) {
        let vis = this;
        vis.svg.selectAll('rect')
        .data(Object.entries(data))
        .join('rect')
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
        .attr('width', vis.x.bandwidth());
    }
    
}
