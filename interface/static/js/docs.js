const toggleBtn = document.getElementById('toggleTable');
const tableWrapper = document.getElementById('themesTableWrapper');

toggleBtn.addEventListener('click', () => {
    tableWrapper.classList.toggle('expanded-table');
    toggleBtn.textContent = tableWrapper.classList.contains('expanded-table') ? 'Collapse Table' : 'Expand Table';
});