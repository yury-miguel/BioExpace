let allDocuments = [];
let filteredDocuments = [];
let currentPage = 1;
const docsPerPage = 6;

document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('/api/documents');
    allDocuments = await response.json();
    filteredDocuments = allDocuments;
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
        container.innerHTML = `<div class="col-12 text-center text-muted"><p>No documents found.</p></div>`;
        return;
    }

    pagedDocs.forEach(doc => {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-4 document-card';

        // Header HTML
        let headerHTML = `
            <div class="card-header">
                <h5 class="doc-title mb-0">${doc.title}</h5>
                <p class="doc-date mb-0"><small>Published: ${doc.date}</small></p>
            </div>
        `;

        let themesHTML = '';
        if (doc.themes && Object.keys(doc.themes).length > 0) {
            themesHTML += `<div class="doc-themes mb-3"><h6 class="section-title">Themes</h6><div class="theme-tags">`;
            for (let theme in doc.themes) {
                themesHTML += `<span class="theme-tag" title="${theme}">${theme}</span>`;
            }
            themesHTML += `</div></div>`;
        }

        let insightsHTML = '';
        if (doc.themes && Object.keys(doc.themes).length > 0) {
            insightsHTML += `<div class="doc-insights"><h6 class="section-title">Insights</h6>`;
            for (let theme in doc.themes) {
                const details = doc.themes[theme];
                insightsHTML += `<div class="theme-insights mb-2"><span class="theme-label">${theme}</span><ul class="insights-list">`;

                // Observations
                if (details.observations && details.observations.length > 0) {
                    details.observations.forEach(obs => {
                        insightsHTML += `<li class="insight-item"><span class="insight-type">Observations:</span> ${obs}</li>`;
                    });
                }

                insightsHTML += `</ul></div>`;
            }
            insightsHTML += `</div>`;
        }

        let footerHTML = `<div class="card-footer"><a href="/document/${doc.id}" class="btn btn-purple w-100">Explore Details</a></div>`;

        card.innerHTML = `
            <div class="card doc-card h-100">
                ${headerHTML}
                <div class="card-body">
                    ${themesHTML}
                    ${insightsHTML}
                </div>
                ${footerHTML}
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

    // First
    const firstLi = document.createElement('li');
    firstLi.className = 'page-item' + (currentPage === 1 ? ' disabled' : '');
    firstLi.innerHTML = `<a class="page-link" href="javascript:displayPage(1)">First</a>`;
    pagination.appendChild(firstLi);

    // Previous
    const prevLi = document.createElement('li');
    prevLi.className = 'page-item' + (currentPage === 1 ? ' disabled' : '');
    prevLi.innerHTML = `<a class="page-link" href="javascript:displayPage(${currentPage - 1})">Previous</a>`;
    pagination.appendChild(prevLi);

    // Page Numbers (show max 5 around current)
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
    startPage = Math.max(1, endPage - maxPagesToShow + 1);

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = 'page-item' + (i === currentPage ? ' active' : '');
        li.innerHTML = `<a class="page-link" href="javascript:displayPage(${i})">${i}</a>`;
        pagination.appendChild(li);
    }

    // Next
    const nextLi = document.createElement('li');
    nextLi.className = 'page-item' + (currentPage === totalPages ? ' disabled' : '');
    nextLi.innerHTML = `<a class="page-link" href="javascript:displayPage(${currentPage + 1})">Next</a>`;
    pagination.appendChild(nextLi);

    // Last
    const lastLi = document.createElement('li');
    lastLi.className = 'page-item' + (currentPage === totalPages ? ' disabled' : '');
    lastLi.innerHTML = `<a class="page-link" href="javascript:displayPage(${totalPages})">Last</a>`;
    pagination.appendChild(lastLi);
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
        d3.select("#wordCloud").html("");
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
    container.html("");

    const width = container.node().clientWidth;
    const height = 180; 
    let margin = {top: 10, right: 10, bottom: 60, left: 40};

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleBand()
        .domain(data.map(d => d.theme))
        .range([margin.left, width - margin.right])
        .padding(0.2);

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

    function wrap(text, width) {
        let maxLines = 0;
        text.each(function() {
            const textEl = d3.select(this),
                words = textEl.text().split(/\s+/).reverse();
            let word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.1,
                y = textEl.attr("y"),
                dy = 0,
                tspan = textEl.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));
                if (tspan.node().getComputedTextLength() > width) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = textEl.append("tspan")
                        .attr("x", 0)
                        .attr("y", y)
                        .attr("dy", ++lineNumber * lineHeight + dy + "em")
                        .text(word);
                }
            }
            if (lineNumber + 1 > maxLines) maxLines = lineNumber + 1;
        });
        return maxLines;
    }

    const xAxisG = svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "0.75rem");

    const maxLines = wrap(xAxisG, x.bandwidth());

    margin.bottom = Math.max(60, maxLines * 14);

    svg.selectAll("g").remove();
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
        .style("text-anchor", "end")
        .style("font-size", "0.75rem")
        .call(wrap, x.bandwidth());

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).ticks(5))
        .selectAll("text")
        .style("font-size", "0.75rem");
}