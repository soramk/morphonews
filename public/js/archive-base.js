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

// Utility function to render news items dynamically using safer DOM methods
function renderNewsCards(newsArray, containerId) {
    const container = document.getElementById(containerId);
    if (!container || !Array.isArray(newsArray)) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create elements using DOM methods for better security
    newsArray.forEach(item => {
        const article = document.createElement('article');
        article.className = 'news-card';
        
        // Title
        const h3 = document.createElement('h3');
        h3.textContent = item.title;
        article.appendChild(h3);
        
        // Description
        const p = document.createElement('p');
        p.textContent = item.description;
        article.appendChild(p);
        
        // Link
        const a = document.createElement('a');
        a.href = item.link;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = 'Read full story ';
        
        // Arrow icon (SVG is safe as it's not user-generated)
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '16');
        svg.setAttribute('height', '16');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('viewBox', '0 0 24 24');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('d', 'M14 5l7 7m0 0l-7 7m7-7H3');
        svg.appendChild(path);
        a.appendChild(svg);
        
        article.appendChild(a);
        container.appendChild(article);
    });
}

// HTML escaping utility - more efficient implementation with complete protection
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;');
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Format timestamp with error handling
function formatTimestamp(isoString) {
    try {
        const date = new Date(isoString);
        if (isNaN(date.getTime())) {
            return isoString; // Return original if invalid
        }
        return date.toLocaleString('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        });
    } catch (e) {
        return isoString; // Fallback to original string
    }
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
