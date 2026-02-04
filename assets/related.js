// Related items functionality for edition pages
async function loadRelatedItems(currentDate, currentTags) {
  try {
    const res = await fetch('/editions/index.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to load editions');
    const editions = await res.json();
    
    // Filter out current edition and find related by tags
    const related = editions
      .filter(edition => edition.date !== currentDate)
      .map(edition => {
        const commonTags = edition.tags?.filter(tag => 
          currentTags.includes(tag)
        ) || [];
        return {
          ...edition,
          score: commonTags.length,
          commonTags
        };
      })
      .filter(edition => edition.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3); // Top 3 related items
    
    return related;
  } catch (error) {
    console.error('Error loading related items:', error);
    return [];
  }
}

function renderRelatedItems(relatedItems, containerId = 'related-items') {
  const container = document.getElementById(containerId);
  if (!container || !relatedItems.length) return;
  
  container.innerHTML = `
    <div class="card">
      <h2 class="h3">Related Editions</h2>
      <p class="muted">Based on shared tags and topics.</p>
      <div class="related-grid">
        ${relatedItems.map(item => `
          <a class="related-item" href="${item.url}">
            <div class="related-date">${item.date}</div>
            <div class="related-title">${item.title}</div>
            <div class="related-summary">${item.summary}</div>
            ${item.commonTags?.length ? `
            <div class="related-tags">
              ${item.commonTags.slice(0, 3).map(tag => `<span class="tag-pill">${tag}</span>`).join('')}
            </div>
            ` : ''}
          </a>
        `).join('')}
      </div>
    </div>
  `;
}

// Initialize related items if on an edition page
if (document.querySelector('.edition-grid')) {
  // Extract current edition date from URL or page
  const pathParts = window.location.pathname.split('/');
  const editionDate = pathParts[pathParts.length - 2] || pathParts[pathParts.length - 1];
  
  // Get tags from meta or data attribute
  const tagsMeta = document.querySelector('meta[name="tags"]');
  const currentTags = tagsMeta ? JSON.parse(tagsMeta.getAttribute('content') || '[]') : [];
  
  if (currentTags.length > 0) {
    // Create container for related items
    const toc = document.querySelector('.toc');
    if (toc) {
      const relatedContainer = document.createElement('div');
      relatedContainer.id = 'related-items';
      toc.parentNode.insertBefore(relatedContainer, toc.nextSibling);
      
      // Load and render related items
      loadRelatedItems(editionDate, currentTags)
        .then(related => renderRelatedItems(related));
    }
  }
}