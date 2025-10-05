async function filterDocuments() {
    const keyword = document.getElementById('keywordFilter').value;
    const response = await fetch(`/api/themes?keyword=${encodeURIComponent(keyword)}`);
    const documents = await response.json();
    const documentList = document.getElementById('documentList');
    documentList.innerHTML = '';

    documents.forEach(doc => {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-4';
        card.innerHTML = `
            <div class="card glass border-gradient h-100 d-flex flex-column justify-content-between">
                <div class="card-body">
                    <h5 class="text-accent mb-2">${doc.title}</h5>
                    <p class="text-sub mb-2"><small>${doc.date || 'Data desconhecida'}</small></p>

                    ${
                        doc.themes && Object.keys(doc.themes).length
                            ? Object.keys(doc.themes)
                                  .map(theme => `<span class="theme-tag">${theme}</span>`)
                                  .join('')
                            : `<p class="text-sub"><i>Sem temas</i></p>`
                    }
                </div>
                <div class="p-3">
                    <a href="/document/${doc.id}" class="btn btn-outline-accent w-100">Explorar</a>
                </div>
            </div>
        `;
        documentList.appendChild(card);
    });
}

async function loadVisualizations() {
    const response = await fetch('/api/themes');
    const themes = await response.json();

    // Word Cloud
    const words = themes.map(t => ({ text: t.theme, size: 20 + Math.random() * 30 }));
    d3.layout.cloud()
        .size([250, 250])
        .words(words)
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .font('Orbitron')
        .fontSize(d => d.size)
        .on('end', drawCloud)
        .start();

    function drawCloud(words) {
        d3.select('#wordCloud').append('svg')
            .attr('width', 250)
            .attr('height', 250)
            .append('g')
            .attr('transform', 'translate(125,125)')
            .selectAll('text')
            .data(words)
            .enter().append('text')
            .style('font-size', d => `${d.size}px`)
            .style('fill', '#b486ff')
            .style('font-family', 'Orbitron')
            .attr('text-anchor', 'middle')
            .attr('transform', d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .text(d => d.text);
    }

    // Bar Chart
    const themeCounts = themes.reduce((acc, t) => {
        acc[t.theme] = (acc[t.theme] || 0) + 1;
        return acc;
    }, {});
    const data = Object.entries(themeCounts).map(([theme, count]) => ({ theme, count }));
    const margin = { top: 20, right: 20, bottom: 70, left: 40 };
    const width = 250 - margin.left - margin.right;
    const height = 250 - margin.top - margin.bottom;

    const svg = d3.select('#barChart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand().range([0, width]).padding(0.1).domain(data.map(d => d.theme));
    const y = d3.scaleLinear().range([height, 0]).domain([0, d3.max(data, d => d.count)]);

    svg.selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.theme))
        .attr('width', x.bandwidth())
        .attr('y', d => y(d.count))
        .attr('height', d => height - y(d.count))
        .attr('fill', 'url(#barGradient)');

    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
        .attr('id', 'barGradient')
        .attr('x1', '0%').attr('x2', '0%')
        .attr('y1', '0%').attr('y2', '100%');
    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#c661ff');
    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#6eb9ff');

    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .style('fill', '#e0e0e0');

    svg.append('g')
        .call(d3.axisLeft(y))
        .style('fill', '#e0e0e0');
}

document.addEventListener('DOMContentLoaded', loadVisualizations);
