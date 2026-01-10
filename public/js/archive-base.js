/**
 * MorphoNews Archive - Common JavaScript
 * Shared functionality across all archive pages
 */

// Initialize Lucide icons when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Utility function to render news items dynamically
function renderNewsCards(newsArray, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !Array.isArray(newsArray)) return;
    
    const newsHTML = newsArray.map(item => `
        <article class="news-card">
            <h3>${escapeHtml(item.title)}</h3>
            <p>${escapeHtml(item.description)}</p>
            <a href="${escapeHtml(item.link)}" target="_blank" rel="noopener noreferrer">
                Read full story
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                </svg>
            </a>
        </article>
    `).join('');
    
    container.innerHTML = newsHTML;
}

// HTML escaping utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Format timestamp
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
}

// Export functions for use in individual archive pages
if (typeof window !== 'undefined') {
    window.MorphoNewsArchive = {
        renderNewsCards,
        scrollToSection,
        formatTimestamp,
        escapeHtml
    };
}
