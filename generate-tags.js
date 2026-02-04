// Tag page generator for StevenAiDigest
const fs = require('fs');
const path = require('path');

async function generateTagPages() {
  try {
    // Read editions index
    const indexPath = path.join(__dirname, 'editions', 'index.json');
    const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
    
    // Collect all tags and their editions
    const tagMap = new Map();
    
    indexData.forEach(edition => {
      const tags = edition.tags || [];
      tags.forEach(tag => {
        if (!tagMap.has(tag)) {
          tagMap.set(tag, []);
        }
        tagMap.get(tag).push(edition);
      });
    });
    
    // Create tags directory if it doesn't exist
    const tagsDir = path.join(__dirname, 'tags');
    if (!fs.existsSync(tagsDir)) {
      fs.mkdirSync(tagsDir, { recursive: true });
    }
    
    // Generate tag index page
    const tagIndexPath = path.join(tagsDir, 'index.html');
    const tagIndexHtml = generateTagIndexHtml(tagMap);
    fs.writeFileSync(tagIndexPath, tagIndexHtml);
    console.log(`Generated tag index: ${tagIndexPath}`);
    
    // Generate individual tag pages
    for (const [tag, editions] of tagMap.entries()) {
      const tagSlug = tag.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      const tagDir = path.join(tagsDir, tagSlug);
      
      if (!fs.existsSync(tagDir)) {
        fs.mkdirSync(tagDir, { recursive: true });
      }
      
      const tagPagePath = path.join(tagDir, 'index.html');
      const tagPageHtml = generateTagPageHtml(tag, editions);
      fs.writeFileSync(tagPagePath, tagPageHtml);
      console.log(`Generated tag page: ${tagPagePath} (${editions.length} editions)`);
    }
    
    console.log(`Generated ${tagMap.size} tag pages`);
    
  } catch (error) {
    console.error('Error generating tag pages:', error);
  }
}

function generateTagIndexHtml(tagMap) {
  const tags = Array.from(tagMap.entries())
    .sort((a, b) => b[1].length - a[1].length); // Sort by edition count
  
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Tags | StevenAiDigest</title>
  <meta name="description" content="Browse StevenAiDigest editions by topic tags." />
  <link rel="alternate" type="application/rss+xml" title="StevenAiDigest" href="/feed.xml" />
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <div class="progress" id="progress"></div>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/">StevenAiDigest</a>
      <nav class="nav">
        <a href="/archive/">Archive</a>
        <a href="/tags/">Tags</a>
      </nav>
    </div>
  </header>

  <main class="wrap prose">
    <h1>Tags</h1>
    <p class="muted">Browse editions by topic. Click any tag to see all related editions.</p>
    
    <div class="archive-tools" aria-label="Tag search">
      <input id="search" class="search" type="search" placeholder="Search tags (e.g. OpenAI, inference, AWS)" />
    </div>
    
    <section class="tags-grid" id="tags-grid">
      ${tags.map(([tag, editions]) => `
        <a class="tag-card" href="/tags/${tag.toLowerCase().replace(/[^a-z0-9]+/g, '-')}/">
          <div class="tag-name">${tag}</div>
          <div class="tag-count">${editions.length} edition${editions.length !== 1 ? 's' : ''}</div>
          <div class="tag-preview">
            ${editions.slice(0, 2).map(edition => `
              <div class="tag-edition">
                <div class="tag-edition-date">${edition.date}</div>
                <div class="tag-edition-title">${edition.title}</div>
              </div>
            `).join('')}
          </div>
        </a>
      `).join('')}
    </section>
    
    <p class="muted"><a href="/archive/">← Back to archive</a></p>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="muted">© <span id="year"></span> StevenAiDigest</div>
    </div>
  </footer>

  <script>
    document.getElementById('year').textContent = new Date().getFullYear();
    
    // Reading progress
    const prog = document.getElementById('progress');
    const onScroll = () => {
      const h = document.documentElement;
      const scrolled = h.scrollTop;
      const max = (h.scrollHeight - h.clientHeight) || 1;
      prog.style.width = (scrolled / max * 100).toFixed(2) + '%';
    };
    document.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    
    // Tag search
    const search = document.getElementById('search');
    const grid = document.getElementById('tags-grid');
    const tagCards = Array.from(grid.querySelectorAll('.tag-card'));
    
    search.addEventListener('input', () => {
      const query = search.value.trim().toLowerCase();
      tagCards.forEach(card => {
        const tagName = card.querySelector('.tag-name').textContent.toLowerCase();
        const shouldShow = !query || tagName.includes(query);
        card.style.display = shouldShow ? 'block' : 'none';
      });
    });
  </script>
</body>
</html>`;
}

function generateTagPageHtml(tag, editions) {
  const sortedEditions = [...editions].sort((a, b) => b.date.localeCompare(a.date));
  
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>${tag} | StevenAiDigest</title>
  <meta name="description" content="StevenAiDigest editions tagged with ${tag}." />
  <link rel="alternate" type="application/rss+xml" title="StevenAiDigest" href="/feed.xml" />
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <div class="progress" id="progress"></div>
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/">StevenAiDigest</a>
      <nav class="nav">
        <a href="/archive/">Archive</a>
        <a href="/tags/">Tags</a>
      </nav>
    </div>
  </header>

  <main class="wrap prose">
    <div class="kicker">Tag</div>
    <h1>${tag}</h1>
    <p class="muted">${editions.length} edition${editions.length !== 1 ? 's' : ''} tagged with ${tag}.</p>
    
    <div class="archive-tools" aria-label="Search within tag">
      <input id="search" class="search" type="search" placeholder="Search within ${tag} editions" />
    </div>
    
    <section class="grid" id="grid">
      ${sortedEditions.map(edition => `
        <a class="tile ${edition.thumbnail ? 'has-thumbnail' : ''}" href="${edition.url}">
          <div class="tile-content">
            <div class="k">${edition.date}</div>
            <div class="t">${edition.title}</div>
            <div class="m">${edition.summary}</div>
            <div class="tags">
              ${(edition.tags || []).filter(t => t !== tag).slice(0, 3).map(t => `
                <a class="tag-pill" href="/tags/${t.toLowerCase().replace(/[^a-z0-9]+/g, '-')}/">${t}</a>
              `).join('')}
              ${(edition.tags || []).length > 4 ? `<span class="tag-pill">+${(edition.tags || []).length - 4}</span>` : ''}
            </div>
          </div>
          ${edition.thumbnail ? `<img class="thumbnail" src="${edition.thumbnail}" alt="${edition.title}" loading="lazy" />` : ''}
        </a>
      `).join('')}
    </section>
    
    <p class="muted">
      <a href="/tags/">← Browse all tags</a> · 
      <a href="/archive/">Back to archive</a>
    </p>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="muted">© <span id="year"></span> StevenAiDigest</div>
    </div>
  </footer>

  <script>
    document.getElementById('year').textContent = new Date().getFullYear();
    
    // Reading progress
    const prog = document.getElementById('progress');
    const onScroll = () => {
      const h = document.documentElement;
      const scrolled = h.scrollTop;
      const max = (h.scrollHeight - h.clientHeight) || 1;
      prog.style.width = (scrolled / max * 100).toFixed(2) + '%';
    };
    document.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    
    // Search within tag
    const search = document.getElementById('search');
    const grid = document.getElementById('grid');
    const tiles = Array.from(grid.querySelectorAll('.tile'));
    
    search.addEventListener('input', () => {
      const query = search.value.trim().toLowerCase();
      tiles.forEach(tile => {
        const title = tile.querySelector('.t').textContent.toLowerCase();
        const summary = tile.querySelector('.m').textContent.toLowerCase();
        const tags = Array.from(tile.querySelectorAll('.tag-pill')).map(pill => pill.textContent.toLowerCase());
        const hay = [title, summary, ...tags].join(' ');
        const shouldShow = !query || hay.includes(query);
        tile.style.display = shouldShow ? 'block' : 'none';
      });
    });
  </script>
</body>
</html>`;
}

// Run if called directly
if (require.main === module) {
  generateTagPages();
}

module.exports = { generateTagPages };