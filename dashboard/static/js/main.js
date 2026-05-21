// ═══════════════════════════════════
//  Dashboard JavaScript
// ═══════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    animateCounters();
    initTooltips();
});

function animateCounters() {
    document.querySelectorAll('.stat-number').forEach(counter => {
        const target = parseInt(counter.textContent.replace(/,/g, ''));
        if (isNaN(target)) return;

        let current = 0;
        const increment = Math.ceil(target / 50);
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = current.toLocaleString();
        }, 30);
    });
}

function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseenter', (e) => {
            const tip = document.createElement('div');
            tip.className = 'tooltip';
            tip.textContent = el.dataset.tooltip;
            document.body.appendChild(tip);

            const rect = el.getBoundingClientRect();
            tip.style.top = `${rect.top - tip.offsetHeight - 8}px`;
            tip.style.left = `${rect.left + (rect.width - tip.offsetWidth) / 2}px`;
        });
        el.addEventListener('mouseleave', () => {
            document.querySelectorAll('.tooltip').forEach(t => t.remove());
        });
    });
}

// Auto-refresh stats
async function refreshStats(guildId) {
    try {
        const resp = await fetch(`/api/stats/${guildId}`);
        const stats = await resp.json();
        console.log('Stats refreshed:', stats);
    } catch (e) {
        console.error('Failed to refresh stats:', e);
    }
}

// Theme toggle
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
    localStorage.setItem('theme', html.getAttribute('data-theme'));
}

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);