# POC Manager Marketing Site

A modern, responsive marketing website for POC Manager - the ultimate platform for managing Proof of Concept projects.

## 🚀 Features

- **Responsive Design**: Works perfectly on all devices (mobile, tablet, desktop)
- **Modern UI**: Built with Tailwind CSS for a clean, professional look
- **Performance Optimized**: Lazy loading, intersection observers, and optimized assets
- **SEO Ready**: Proper meta tags and semantic HTML
- **Accessible**: WCAG 2.1 compliant with keyboard navigation support

## 📁 Structure

```
marketing-site/
├── index.html          # Main landing page
├── config.js           # Configuration (demo URL, contact info)
├── assets/
│   ├── style.css       # Custom CSS and animations
│   └── script.js       # JavaScript functionality
└── images/             # Screenshots and graphics (add your own)
    ├── dashboard-screenshot.png
    ├── workflow-diagram.png
    ├── sales-engineer-view.png
    └── customer-view.png
```

## 🎨 Sections

1. **Hero Section**: Eye-catching headline with CTA button
2. **Stats Section**: Key metrics and achievements
3. **Features Section**: 6 main feature cards
4. **How It Works**: 4-step workflow explanation
5. **Benefits Section**: Value proposition for sales engineers and customers
6. **Testimonials**: Social proof from satisfied users
7. **Pricing**: 3 pricing tiers (Demo, Professional, Enterprise)
8. **CTA Section**: Final conversion opportunity
9. **Footer**: Links and company information

## ⚙️ Configuration

Edit `config.js` to customize:

```javascript
const CONFIG = {
    DEMO_REQUEST_URL: 'http://localhost:5173/demo-request',  // Change this!
    APP_URL: 'http://localhost:5173',
    CONTACT_EMAIL: 'sales@pocmanager.io',
    SUPPORT_EMAIL: 'support@pocmanager.io',
    SOCIAL: {
        twitter: 'https://twitter.com/pocmanager',
        linkedin: 'https://linkedin.com/company/pocmanager',
        github: 'https://github.com/pocmanager'
    }
};
```

## 🖼️ Adding Screenshots

Replace the placeholder images in the `images/` directory with actual screenshots:

1. **dashboard-screenshot.png** (800x600px): Main dashboard view
2. **workflow-diagram.png** (1200x400px): POC workflow illustration
3. **sales-engineer-view.png** (800x600px): Sales engineer perspective
4. **customer-view.png** (800x600px): Customer portal view

### Recommended Image Specs:
- Format: PNG or WebP
- Compression: Optimized for web
- Max file size: 500KB per image
- Include descriptive alt text

## 🌐 Deployment

### Option 1: Static Hosting (Vercel, Netlify)

1. Push to GitHub repository
2. Connect to Vercel/Netlify
3. Deploy (automatic)

### Option 2: CDN (Cloudflare Pages)

1. Upload files to Cloudflare Pages
2. Configure custom domain
3. Enable caching

### Option 3: S3 + CloudFront

1. Upload to S3 bucket
2. Configure CloudFront distribution
3. Point DNS to CloudFront URL

### Option 4: Self-hosted

Serve with any web server (nginx, Apache, etc.):

```bash
# Example with Python
python3 -m http.server 8080

# Example with Node.js
npx serve .
```

## 🎯 SEO Optimization

The site includes:
- Semantic HTML5 structure
- Meta description and title tags
- Open Graph tags for social sharing
- Proper heading hierarchy (H1 → H6)
- Alt text for all images
- Fast loading times

### Next Steps for SEO:
1. Add Open Graph and Twitter Card meta tags
2. Create sitemap.xml
3. Add robots.txt
4. Implement structured data (JSON-LD)
5. Set up Google Analytics/Plausible

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🔧 Customization

### Colors

Edit Tailwind colors in `style.css`:

```css
:root {
    --primary-color: #4f46e5;
    --secondary-color: #9333ea;
    --success-color: #10b981;
    --warning-color: #f59e0b;
}
```

### Fonts

To add custom fonts, include Google Fonts in `<head>`:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

Then update Tailwind config or add CSS:

```css
body {
    font-family: 'Inter', sans-serif;
}
```

### Content

All text content is in `index.html` and can be edited directly. No build process required!

## 📊 Analytics

To add analytics, insert tracking code before `</body>`:

### Google Analytics
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Plausible (Privacy-friendly)
```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## 🚦 Performance Tips

1. **Optimize Images**: Use WebP format, compress with TinyPNG
2. **Minify Assets**: Minify CSS/JS for production
3. **Enable Caching**: Configure proper cache headers
4. **Use CDN**: Serve static assets from CDN
5. **Lazy Load**: Already implemented for images

## 🐛 Troubleshooting

**Issue**: Demo button not working
- Solution: Check `config.js` has correct `DEMO_REQUEST_URL`

**Issue**: Images not loading
- Solution: Ensure image files exist in `images/` directory with correct names

**Issue**: Mobile menu not toggling
- Solution: Verify `script.js` is loaded after page content

## 📝 License

This marketing site is part of the POC Manager project.

## 🤝 Contributing

To improve the marketing site:
1. Edit HTML/CSS/JS directly
2. Test on multiple devices/browsers
3. Optimize images before committing
4. Update this README with changes

## 📞 Support

For questions about the marketing site:
- Email: support@pocmanager.io
- GitHub Issues: [Create an issue](https://github.com/pocmanager/issues)

---

Built with ❤️ for POC Manager
