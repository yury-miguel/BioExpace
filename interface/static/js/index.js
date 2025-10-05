let allDocuments = [];
let filteredDocuments = [];
let currentPage = 1;
const docsPerPage = 12;

document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('/api/documents');
    allDocuments = await response.json();
    filteredDocuments = allDocuments;  // start with full dataset
    displayPage(1);
    buildBarChart();
    buildWordCloud();
});

function filterDocuments() {
    const keyword = document.getElementById('keywordFilter').value.toLowerCase();
    filteredDocuments = allDocuments.filter(doc => 
        doc.title.toLowerCase().includes(keyword) ||
        Object.keys(doc.themes).some(t => t.toLowerCase().includes(keyword))
    );
    displayPage(1);
}

function displayPage(page) {
    currentPage = page;
    const start = (page - 1) * docsPerPage;
    const end = start + docsPerPage;
    const pagedDocs = filteredDocuments.slice(start, end);

    const container = document.getElementById('documentList');
    container.innerHTML = '';

    if (pagedDocs.length === 0) {
        container.innerHTML = `<p class="text-muted">No documents found.</p>`;
    }

    pagedDocs.forEach(doc => {
        const card = document.createElement('div');
        card.className = 'col-md-6 mb-4 document-card';
        let themesHTML = '';
        for (let theme in doc.themes) {
            const points = doc.themes[theme].points.slice(0,2).map(p => `<li>${p}</li>`).join('');
            themesHTML += `<span class="theme-tag" title="${theme}">${theme}</span><ul>${points}</ul>`;
        }
        card.innerHTML = `
            <div class="card doc-card h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="doc-title">${doc.title}</h5>
                    <p class="doc-date"><small>${doc.date}</small></p>
                    <div class="doc-insights mb-2">${themesHTML}</div>
                    <a href="/document/${doc.id}" class="btn btn-purple mt-auto">Explore</a>
                </div>
            </div>
        `;
        container.appendChild(card);
    });

    buildPagination();
}

function buildPagination() {
    const totalPages = Math.ceil(filteredDocuments.length / docsPerPage);
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = 'page-item' + (i === currentPage ? ' active' : '');
        li.innerHTML = `<a class="page-link" href="javascript:displayPage(${i})">${i}</a>`;
        pagination.appendChild(li);
    }
}

async function buildWordCloud() {
    const response = await fetch('/api/themes/all');
    const themesData = await response.json();
    const words = Object.keys(themesData).map(theme => ({text: theme, size: 10 + themesData[theme] * 3}));

    const layout = d3.layout.cloud()
        .size([250, 250])
        .words(words)
        .padding(5)
        .rotate(() => 0)
        .fontSize(d => d.size)
        .on("end", drawWordCloud);

    layout.start();

    function drawWordCloud(words) {
        d3.select("#wordCloud").html(""); // clear previous
        d3.select("#wordCloud").append("svg")
            .attr("width", 250)
            .attr("height", 250)
            .append("g")
            .attr("transform", "translate(125,125)")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", d => d.size + "px")
            .style("fill", "#6e0eff")
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .text(d => d.text);
    }
}

async function buildBarChart() {
    const response = await fetch('/api/themes/all');
    const themesData = await response.json();
    const data = Object.entries(themesData).map(([theme, count]) => ({theme, count}));

    const container = d3.select("#barChart");
    container.html(""); // clear previous

    const width = 250, height = 250, margin = {top: 20, right: 10, bottom: 50, left: 40};

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleBand()
        .domain(data.map(d => d.theme))
        .range([margin.left, width - margin.right])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count)]).nice()
        .range([height - margin.bottom, margin.top]);

    svg.append("g")
        .attr("fill", "#6e0eff")
        .selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", d => x(d.theme))
        .attr("y", d => y(d.count))
        .attr("height", d => y(0) - y(d.count))
        .attr("width", x.bandwidth());

    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));
}
