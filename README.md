# Municipal-Bulletin

地方自治体の広報誌データベースです。`csv/` フォルダに CSV 形式で記事データを保管しています。

## 検索ページ

`docs/` フォルダが GitHub Pages として公開され、`docs/index.html` から検索ページを利用できます。検索ページではインデックス (`docs/index.json`) を読み込み、キーワード検索を行います。記事の本文は必要に応じて CSV から取得し Markdown 形式で表示・ダウンロードできます。

## インデックスの更新

CSV ファイルが追加・変更されると GitHub Actions (`.github/workflows/update-index.yml`) が実行され、`scripts/update_index.py` を用いてインデックスを再生成します。OpenAI API キー (`OPENAI_API_KEY`) が設定されている場合は LLM を利用して要約とタグ付けを行います。キーがない場合は簡易的な処理で代替します。

### 手動で実行する場合

```bash
pip install -r requirements.txt
python scripts/update_index.py
```

生成された `docs/index.json` をコミットしてください。
