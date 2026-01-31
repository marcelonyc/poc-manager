// POC Manager Marketing Site JavaScript

// Request Demo Function
function requestDemo() {
    window.location.href = CONFIG.DEMO_REQUEST_URL;
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close mobile menu when clicking a link
document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuLinks = document.querySelectorAll('#mobile-menu a');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', () => {
            const menu = document.getElementById('mobile-menu');
            if (menu) {
                menu.classList.add('hidden');
            }
        });
    });

    // Initialize intersection observer for scroll animations
    initScrollAnimations();

    // Add scroll event listener for navbar
    handleNavbarScroll();

    // Initialize stats counter animation
    initStatsCounter();

    // Handle form submissions
    initFormHandlers();
});

// Intersection Observer for scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);

    // Observe all elements with 'reveal' class
    document.querySelectorAll('.reveal').forEach(element => {
        observer.observe(element);
    });
}

// Navbar scroll effect
function handleNavbarScroll() {
    const navbar = document.querySelector('nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            navbar.classList.remove('shadow-lg');
        } else {
            navbar.classList.add('shadow-lg');
        }

        lastScroll = currentScroll;
    });
}

// Animated stats counter
function initStatsCounter() {
    const stats = document.querySelectorAll('.stat-item');
    let animated = false;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animated) {
                animateStats();
                animated = true;
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => observer.observe(stat));
}

function animateStats() {
    const stats = [
        { element: document.querySelector('.stat-item:nth-child(1) .text-4xl'), target: 500, suffix: '+' },
        { element: document.querySelector('.stat-item:nth-child(2) .text-4xl'), target: 10000, suffix: '+' },
        { element: document.querySelector('.stat-item:nth-child(3) .text-4xl'), target: 95, suffix: '%' },
        { element: document.querySelector('.stat-item:nth-child(4) .text-4xl'), target: 24, suffix: '/7' }
    ];

    stats.forEach(({ element, target, suffix }) => {
        if (!element) return;

        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, 40);
    });
}

// Form handlers
function initFormHandlers() {
    // Newsletter form
    const newsletterForm = document.querySelector('#newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubmit);
    }

    // Contact form
    const contactForm = document.querySelector('#contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }
}

function handleNewsletterSubmit(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;

    // Here you would typically send this to your backend
    console.log('Newsletter signup:', email);
    alert('Thank you for subscribing! Check your email for confirmation.');
    e.target.reset();
}

function handleContactSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    // Here you would typically send this to your backend
    console.log('Contact form submission:', Object.fromEntries(formData));
    alert('Thank you for your message! We\'ll get back to you soon.');
    e.target.reset();
}

// Add click tracking for analytics (placeholder)
document.addEventListener('click', function (e) {
    const target = e.target.closest('a, button');
    if (target) {
        const action = target.getAttribute('data-track') || target.textContent.trim();
        // Send to analytics service
        console.log('Track:', action);
    }
});

// Handle pricing card selection
function selectPlan(planName) {
    console.log('Selected plan:', planName);
    if (planName === 'Enterprise') {
        window.location.href = `mailto:${CONFIG.CONTACT_EMAIL}?subject=Enterprise Plan Inquiry`;
    } else {
        requestDemo();
    }
}

// Copy to clipboard function (for code snippets if needed)
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white transform transition-all duration-300`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.transform = 'translateY(-100px)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Lazy loading for images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Handle video play on scroll into view
function initVideoHandlers() {
    const videos = document.querySelectorAll('video[data-autoplay]');

    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            if (entry.isIntersecting) {
                video.play();
            } else {
                video.pause();
            }
        });
    }, { threshold: 0.5 });

    videos.forEach(video => videoObserver.observe(video));
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initVideoHandlers();
});

// Prevent FOUC (Flash of Unstyled Content)
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Handle keyboard navigation
document.addEventListener('keydown', (e) => {
    // ESC key closes mobile menu
    if (e.key === 'Escape') {
        const menu = document.getElementById('mobile-menu');
        if (menu && !menu.classList.contains('hidden')) {
            menu.classList.add('hidden');
        }
    }
});

// Performance monitoring (optional)
if ('performance' in window) {
    window.addEventListener('load', () => {
        const perfData = performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log('Page load time:', pageLoadTime, 'ms');
    });
}

// Service Worker registration (for PWA features if needed)
if ('serviceWorker' in navigator) {
    // Uncomment when you have a service worker file
    // navigator.serviceWorker.register('/sw.js')
    //     .then(reg => console.log('Service Worker registered'))
    //     .catch(err => console.error('Service Worker registration failed:', err));
}

// Export functions for use in HTML onclick attributes
window.requestDemo = requestDemo;
window.scrollToSection = scrollToSection;
window.toggleMobileMenu = toggleMobileMenu;
window.selectPlan = selectPlan;
window.copyToClipboard = copyToClipboard;
