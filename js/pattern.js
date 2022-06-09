class Patternvis {
    constructor(_data) {
        this.config = {
            width: 800,
            height: 500,
            margin: 40
        }
        this.data = _data;
        this.initVis();
    }
    initVis() {
        let vis = this;
        
        vis.svg = d3.select('#patternView')
        .append('svg')
        .attr('width', vis.config.width)
        .attr('height', vis.config.height)
        .append('g')
        .attr('class', 'patternVisArea')
        .attr('transform', `translate(${vis.config.margin}, ${vis.config.margin - 20})`)

        let x = d3.scalePoint()
        .domain([0, 1, 2, 3, 4, 5])
        .range([0, vis.config.width])

        let y = d3.scaleLinear()
        .range([vis.config.height - vis.config.margin, 0])
        .domain([0, 1000])

        vis.svg.append('g')
        .attr('class', 'yAxis')
        .call(d3.axisLeft(y));
        vis.svg.append('g')
        .attr('class', 'xAxis')
        .call(d3.axisBottom(x))
        .attr('transform', `translate(0, ${vis.config.height - vis.config.margin})`)
    }
    updateVis(data) {
        let vis = this;
        vis.renderVis(data);
    }

    renderVis(data) {
        
    }
    
}
