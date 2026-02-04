// Update all edition pages with tags navigation and related items
const fs = require('fs');
const path = require('path');

async function updateEditionPages() {
  try {
    // Read editions index to get all edition paths
    const indexPath = path.join(__dirname, 'editions', 'index.json');
    const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
    
    for (const edition of indexData) {
      const editionPath = edition.url.replace(/^\//, ''); // Remove leading slash
      const htmlPath = path.join(__dirname, editionPath, 'index.html');
      
      if (fs.existsSync(htmlPath)) {
        let html = fs.readFileSync(htmlPath, 'utf8');
        
        // Update navigation to include tags
        html = html.replace(
          /<nav class="nav">\s*<a href="\/archive\/">Archive<\/a>\s*<\/nav>/,
          '<nav class="nav">\n        <a href="/archive/">Archive</a>\n        <a href="/tags/">Tags</a>\n      </nav>'
        );
        
        // Add meta tags if not present
        if (edition.tags && edition.tags.length > 0) {
          const tagsMeta = `<meta name="tags" content='${JSON.stringify(edition.tags)}' />`;
          
          if (!html.includes('name="tags"')) {
            // Insert after description meta
            html = html.replace(
              /<meta name="description" content="[^"]+" \/>/,
              `$&\n  ${tagsMeta}`
            );
          }
        }
        
        // Add related.js script if not present
        if (!html.includes('/assets/related.js')) {
          // Insert before closing body tag
          html = html.replace(
            /<\/body>/,
            '  <script src="/assets/related.js"></script>\n</body>'
          );
        }
        
        fs.writeFileSync(htmlPath, html);
        console.log(`Updated: ${editionPath}`);
      }
    }
    
    console.log('Updated all edition pages');
    
  } catch (error) {
    console.error('Error updating edition pages:', error);
  }
}

// Run if called directly
if (require.main === module) {
  updateEditionPages();
}

module.exports = { updateEditionPages };