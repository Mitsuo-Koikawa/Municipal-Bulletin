import os
import json
import glob
import pandas as pd
import openai
from typing import List

# Directory containing CSV files
CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csv')
OUTPUT_JSON = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'index.json')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def summarize(text: str) -> str:
    text = text.strip().replace('\n', ' ')
    if not text:
        return ""
    if OPENAI_API_KEY:
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Summarize the following Japanese text in one sentence."},
                         {"role": "user", "content": text[:4000]}],
                max_tokens=60
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print("openai error", e)
    # fallback simple summary
    return text[:120] + ("..." if len(text) > 120 else "")

def extract_tags(text: str) -> List[str]:
    if OPENAI_API_KEY:
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "日本語テキストを読んで重要なキーワードを最大5個抽出してください。結果はカンマ区切りで返してください。"},
                         {"role": "user", "content": text[:4000]}],
                max_tokens=20
            )
            line = resp.choices[0].message.content.strip()
            return [t.strip() for t in line.split(',') if t.strip()]
        except Exception as e:
            print("openai error", e)
    # fallback: naive tag extraction using top words
    words = [w for w in text.replace('\n', ' ').split(' ') if len(w) > 3]
    seen = []
    for w in words:
        if w not in seen:
            seen.append(w)
        if len(seen) == 5:
            break
    return seen


def detect_encoding(path: str) -> str:
    with open(path, 'rb') as f:
        data = f.read(4000)
    try:
        import chardet
        enc = chardet.detect(data)
        return enc['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'


def load_csv(path: str) -> pd.DataFrame:
    enc = detect_encoding(path)
    return pd.read_csv(path, encoding=enc)


def build_index() -> list:
    entries = []
    for file in sorted(glob.glob(os.path.join(CSV_DIR, '*.csv'))):
        df = load_csv(file)
        for i, row in df.iterrows():
            article_text = str(row.get('記事本文', ''))
            entry = {
                'id': f"{os.path.basename(file)}-{i}",
                'municipality': str(row.get('自治体名', '')),
                'date': str(row.get('公開年月', '')),
                'issue_title': str(row.get('発行号タイトル', '')),
                'article_title': str(row.get('記事タイトル', '')),
                'category': str(row.get('カテゴリ', '')),
                'summary': summarize(article_text),
                'tags': extract_tags(article_text),
                'source': os.path.relpath(file, os.path.dirname(OUTPUT_JSON)),
                'row': i + 1
            }
            entries.append(entry)
    return entries


def main():
    entries = build_index()
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(entries)} entries to {OUTPUT_JSON}")


if __name__ == '__main__':
    main()
