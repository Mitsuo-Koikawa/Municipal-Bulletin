async function loadIndex() {
  const res = await fetch('index.json');
  return await res.json();
}

function createMarkdown(entry, article) {
  return `# ${entry.article_title}\n\n- 自治体: ${entry.municipality}\n- 日付: ${entry.date}\n- 号: ${entry.issue_title}\n- カテゴリ: ${entry.category}\n\n${article}`;
}

async function fetchArticle(entry) {
  const res = await fetch(entry.source);
  const text = await res.text();
  const parsed = Papa.parse(text, {header:true});
  const row = parsed.data[entry.row-1];
  return row['記事本文'] || '';
}

function download(name, content) {
  const blob = new Blob([content], {type: 'text/markdown'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

async function search(entries, query) {
  query = query.trim();
  if(!query) return [];
  return entries.filter(e =>
    e.article_title.includes(query) ||
    e.summary.includes(query) ||
    (e.tags && e.tags.join(' ').includes(query)) ||
    e.category.includes(query)
  );
}

window.addEventListener('DOMContentLoaded', async () => {
  const entries = await loadIndex();
  document.getElementById('searchBtn').addEventListener('click', async () => {
    const q = document.getElementById('query').value;
    const results = await search(entries, q);
    const container = document.getElementById('results');
    container.innerHTML = '';
    for(let i=0; i<Math.min(results.length, 15); i++) {
      const e = results[i];
      const div = document.createElement('div');
      div.className = 'result';
      div.innerHTML = `<h3>${e.article_title}</h3><p>${e.summary}</p>`;
      const btn = document.createElement('button');
      btn.textContent = '表示・ダウンロード';
      btn.addEventListener('click', async () => {
        const article = await fetchArticle(e);
        const md = createMarkdown(e, article);
        const pre = document.createElement('pre');
        pre.className = 'markdown';
        pre.textContent = md;
        div.appendChild(pre);
        download(`${e.id}.md`, md);
      });
      div.appendChild(btn);
      container.appendChild(div);
    }
  });
});
