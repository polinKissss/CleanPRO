const input = document.getElementById('live-search');
const panel = document.getElementById('live-results');
const list = document.getElementById('live-list');
const status = document.getElementById('live-status');
let timer = null;

if (input && panel) {
    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) {
            panel.hidden = true;
            return;
        }
        timer = setTimeout(async () => {
            status.textContent = 'Ищем…';            
            panel.hidden = false;
            list.innerHTML = '';
            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(q)}`);
                const data = await response.json();
                status.textContent = data.results.length
                    ? `Найдено: ${data.results.length}`
                    : 'Ничего не найдено';
                for (const item of data.results) {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="${item.url}"><strong>${item.name}</strong><br>${item.description}</a>`;
                    list.appendChild(li);
                }
            } catch {
                status.textContent = 'Ошибка поиска, попробуйте ещё раз';
            }
        }, 300);  
    });

    document.addEventListener('click', (e) => {
        if (!panel.contains(e.target) && e.target !== input) panel.hidden = true;
    });
}
const grid = document.querySelector('.services-grid');
document.querySelectorAll('.sort-bar [data-sort]').forEach(btn => {
    btn.addEventListener('click', () => {
        if (!grid) return;
        const cards = [...grid.querySelectorAll('.service-card')];
        cards.sort((a, b) => btn.dataset.sort === 'labor'
            ? parseFloat(a.dataset.labor) - parseFloat(b.dataset.labor)
            : a.dataset.name.localeCompare(b.dataset.name, 'ru'));
        cards.forEach(card => grid.appendChild(card));  
    });
});

