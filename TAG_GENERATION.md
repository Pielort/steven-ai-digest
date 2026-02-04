# Tag Page Generation

## Overview
The tag system automatically generates browseable tag pages from the `editions/index.json` file.

## How It Works

1. **Data Source**: Reads `editions/index.json` to get all editions with their tags
2. **Tag Collection**: Groups editions by tag
3. **Page Generation**: Creates:
   - `tags/index.html` - Browse all tags
   - `tags/<tag-slug>/index.html` - Individual tag pages

## Usage

### Generate Tag Pages
```bash
node generate-tags.js
```

This will create/update all tag pages in the `tags/` directory.

### Update Edition Pages
```bash
node update-edition-pages.js
```

This updates all edition pages with:
- Tags navigation link
- Meta tags for related items
- Related.js script inclusion

## Adding New Editions

When adding a new edition:

1. Add the edition to `editions/index.json` with:
   ```json
   {
     "date": "YYYY-MM-DD",
     "year": "YYYY",
     "title": "Edition YYYY-MM-DD",
     "url": "/editions/YYYY-MM-DD/",
     "summary": "Brief summary",
     "tags": ["tag1", "tag2", "tag3"],
     "thumbnail": "/assets/visuals/web/chart-slide.webp"
   }
   ```

2. Run tag generation:
   ```bash
   node generate-tags.js
   ```

3. The new edition will automatically appear on:
   - Archive page with tags and thumbnail
   - Relevant tag pages
   - As related items on other edition pages

## Tag Page Features

### Tag Index (`/tags/`)
- Browse all tags sorted by edition count
- Search tags by name
- Shows preview of recent editions for each tag

### Individual Tag Pages (`/tags/<tag>/`)
- All editions with that tag
- Search within tag editions
- Related tags from each edition
- Consistent styling with archive

## Related Items System

Edition pages automatically show related editions based on shared tags. The system:
1. Reads tags from the page's meta tag
2. Fetches all editions from `index.json`
3. Calculates similarity based on shared tags
4. Displays top 3 related editions in sidebar

## Maintenance

The system is designed to be low-maintenance:
- No database required
- Static file generation
- Fast client-side search
- Easy to extend with new features