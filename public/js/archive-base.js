/**
 * MorphoNews Archive - Common JavaScript
 * Shared functionality across all archive pages
 */

// Style Management - Load and apply saved style preference
const STYLE_STORAGE_KEY = 'morphonews_selected_style';
const DEFAULT_STYLE = 'default';

function loadStylePreference() {
    try {
        return localStorage.getItem(STYLE_STORAGE_KEY) || DEFAULT_STYLE;
    } catch (e) {
        return DEFAULT_STYLE;
    }
}

function saveStylePreference(styleId) {
    try {
        localStorage.setItem(STYLE_STORAGE_KEY, styleId);
    } catch (e) {
        console.warn('Failed to save style preference:', e);
    }
}

function applyStyle(styleId) {
    // Validate styleId to prevent path traversal
    if (styleId && !/^[a-z-]+$/.test(styleId)) {
        console.warn('Invalid style ID:', styleId);
        return;
    }
    
    // Remove any existing style overrides
    const existingLink = document.getElementById('dynamic-style');
    if (existingLink) {
        existingLink.remove();
    }
    
    // Apply new style if not default
    if (styleId && styleId !== DEFAULT_STYLE) {
        const link = document.createElement('link');
        link.id = 'dynamic-style';
        link.rel = 'stylesheet';
        link.href = `../styles/archives/${styleId}.css`;
        document.head.appendChild(link);
    }
    
    // Save preference
    saveStylePreference(styleId);
    
    // Update active state in style selector if it exists
    updateStyleSelectorUI(styleId);
}

function updateStyleSelectorUI(activeStyleId) {
    const buttons = document.querySelectorAll('.style-option');
    buttons.forEach(btn => {
        if (btn.dataset.style === activeStyleId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Initialize Lucide icons and apply saved style when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Apply saved style preference
    const savedStyle = loadStylePreference();
    applyStyle(savedStyle);
    
    // Initialize style selector if present
    initStyleSelector();
    
    // Initialize reading features
    initReadingProgress();
    initFontSizeControls();
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
        
        // Link with URL validation
        const a = document.createElement('a');
        // Validate URL is safe (http/https only)
        try {
            const url = new URL(item.link);
            if (url.protocol === 'http:' || url.protocol === 'https:') {
                a.href = item.link;
            } else {
                a.href = '#'; // Fallback for unsafe protocols
            }
        } catch (e) {
            a.href = '#'; // Invalid URL fallback
        }
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
        escapeHtml,
        applyStyle,
        loadStylePreference
    };
}

// Style Selector Initialization
function initStyleSelector() {
    // Fetch available styles
    fetch('../styles/styles.json')
        .then(response => response.json())
        .then(data => {
            renderStyleSelector(data.styles);
        })
        .catch(error => {
            console.warn('Failed to load styles:', error);
        });
}

function renderStyleSelector(styles) {
    const container = document.getElementById('style-selector-grid');
    if (!container) return;
    
    const savedStyle = loadStylePreference();
    
    styles.forEach(style => {
        const button = document.createElement('button');
        button.className = 'style-option';
        button.dataset.style = style.id;
        if (style.id === savedStyle) {
            button.classList.add('active');
        }
        
        // Create preview circles
        const preview = document.createElement('div');
        preview.className = 'style-preview';
        
        const circle1 = document.createElement('div');
        circle1.className = 'preview-circle';
        circle1.style.backgroundColor = style.preview_colors.primary;
        
        const circle2 = document.createElement('div');
        circle2.className = 'preview-circle';
        circle2.style.backgroundColor = style.preview_colors.secondary;
        
        preview.appendChild(circle1);
        preview.appendChild(circle2);
        
        // Create text content
        const name = document.createElement('div');
        name.className = 'style-name';
        name.textContent = style.name;
        
        const desc = document.createElement('div');
        desc.className = 'style-desc';
        desc.textContent = style.description;
        
        button.appendChild(preview);
        button.appendChild(name);
        button.appendChild(desc);
        
        // Add click handler
        button.addEventListener('click', () => {
            applyStyle(style.id);
        });
        
        container.appendChild(button);
    });
}

// Reading Progress Indicator
function initReadingProgress() {
    const progressBar = document.getElementById('reading-progress');
    if (!progressBar) return;
    
    window.addEventListener('scroll', () => {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.scrollY;
        const progress = (scrolled / documentHeight) * 100;
        progressBar.style.width = Math.min(progress, 100) + '%';
    });
}

// Font Size Adjustment
function initFontSizeControls() {
    const FONT_SIZE_KEY = 'morphonews_font_size';
    const increaseBtn = document.getElementById('font-increase');
    const decreaseBtn = document.getElementById('font-decrease');
    const resetBtn = document.getElementById('font-reset');
    
    if (!increaseBtn || !decreaseBtn) return;
    
    // Load saved font size with proper validation
    let fontSize = parseInt(localStorage.getItem(FONT_SIZE_KEY) || '100') || 100;
    applyFontSize(fontSize);
    
    increaseBtn.addEventListener('click', () => {
        fontSize = Math.min(fontSize + 10, 150);
        applyFontSize(fontSize);
        localStorage.setItem(FONT_SIZE_KEY, fontSize.toString());
    });
    
    decreaseBtn.addEventListener('click', () => {
        fontSize = Math.max(fontSize - 10, 70);
        applyFontSize(fontSize);
        localStorage.setItem(FONT_SIZE_KEY, fontSize.toString());
    });
    
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            fontSize = 100;
            applyFontSize(fontSize);
            localStorage.setItem(FONT_SIZE_KEY, fontSize.toString());
        });
    }
}

function applyFontSize(percentage) {
    document.documentElement.style.fontSize = percentage + '%';
}
