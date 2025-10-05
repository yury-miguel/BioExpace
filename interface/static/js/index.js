let allDocuments = [];
let currentPage = 1;
const docsPerPage = 12;

document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('/api/documents'); // Create this endpoint to return all documents
    allDocuments = await response.json();
    displayPage(currentPage);
    buildWordCloud();
    buildBarChart();
});

function filterDocuments() {
    const keyword = document.getElementById('keywordFilter').value.toLowerCase();
    const filtered = allDocuments.filter(doc => 
        doc.title.toLowerCase().includes(keyword) || 
        Object.keys(doc.themes).some(t => t.toLowerCase().includes(keyword))
    );
    displayPage(1, filtered);
}

function displayPage(page, docs = allDocuments) {
    currentPage = page;
    const start = (page - 1) * docsPerPage;
    const end = start + docsPerPage;
    const pagedDocs = docs.slice(start, end);
    
    const container = document.getElementById('documentList');
    container.innerHTML = '';

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

    buildPagination(docs.length);
}

function buildPagination(totalDocs) {
    const totalPages = Math.ceil(totalDocs / docsPerPage);
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    for (let i=1; i<=totalPages; i++) {
        const li = document.createElement('li');
        li.className = 'page-item' + (i === currentPage ? ' active' : '');
        li.innerHTML = `<a class="page-link" href="javascript:displayPage(${i})">${i}</a>`;
        pagination.appendChild(li);
    }
}

function buildWordCloud() {
    // Fetch themes and draw word cloud (similar to your previous D3 code)
}

function buildBarChart() {
    // Fetch themes and draw bar chart
}
