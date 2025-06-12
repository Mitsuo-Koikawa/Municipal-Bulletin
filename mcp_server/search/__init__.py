import json
import os
import re
import pandas as pd
import azure.functions as func

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'docs', 'index.json')
CSV_DIR = os.path.join(BASE_DIR, 'csv')

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    INDEX = json.load(f)

SYNONYMS = {
    '移住': ['移住', '住み替え', '移転'],
    '空き家': ['空き家', '空家']
}

def parse_query(q: str):
    order = None
    if '新しい順' in q:
        order = 'desc'
    if '古い順' in q:
        order = 'asc'
    q = re.sub(r'新しい順.*|古い順.*|の記事.*|を.*$', '', q)
    words = [w for w in re.split(r'[\s,とや]+', q) if w]
    return words, order


def expand_groups(words):
    return [SYNONYMS.get(w, [w]) for w in words]


def includes_any(text: str, arr):
    return any(a in text for a in arr)


def entry_matches(entry, groups):
    text = ' '.join([
        entry.get('article_title', ''),
        entry.get('summary', ''),
        ' '.join(entry.get('tags', [])),
        entry.get('category', '')
    ])
    return all(includes_any(text, g) for g in groups)


def to_date(s: str):
    s = s.replace('.', '-')
    try:
        return pd.to_datetime(s)
    except Exception:
        return pd.Timestamp(0)


def search_entries(entries, q):
    words, order = parse_query(q.strip())
    if not words:
        return []
    groups = expand_groups(words)
    results = [e for e in entries if entry_matches(e, groups)]
    if order:
        results.sort(key=lambda e: to_date(e['date']), reverse=(order == 'desc'))
    return results


def fetch_article(entry):
    path = os.path.join(BASE_DIR, entry['source'])
    df = pd.read_csv(path)
    row = df.iloc[entry['row'] - 1]
    return row.get('記事本文', '')


def create_markdown(entry, article):
    return f"# {entry['article_title']}\n\n- 自治体: {entry['municipality']}\n- 日付: {entry['date']}\n- 号: {entry['issue_title']}\n- カテゴリ: {entry['category']}\n\n{article}"


def build_markdown(results):
    out = ''
    for e in results:
        article = fetch_article(e)
        out += create_markdown(e, article) + '\n\n'
    return out.strip()


def main(req: func.HttpRequest) -> func.HttpResponse:
    q = req.params.get('q') or req.get_json().get('q') if req.get_body() else None
    if not q:
        return func.HttpResponse('missing query', status_code=400)

    results = search_entries(INDEX, q)
    format_md = req.params.get('format') == 'markdown'
    limited = results[:20]

    if format_md:
        md = build_markdown(limited)
        return func.HttpResponse(md, mimetype='text/markdown')
    else:
        body = json.dumps(limited, ensure_ascii=False)
        return func.HttpResponse(body, mimetype='application/json')
