# showdown/tools

Pokemon Showdown のリプレイ HTML を日本語化するためのツール。

## 何をするもの？

`showdown/win/*.html` と `showdown/lose/*.html`（Pokemon Showdown からダウンロードしたリプレイの静的 HTML）に対して、下部に表示される **静的バトルログ** のポケモン名・技・特性・道具・メッセージ類を日本語に置換する。

## なぜ上部のアニメーション部分は英語のままか

各リプレイ HTML には `<script type="text/plain" class="battle-log-data">` ブロックが含まれており、Pokemon Showdown の再生プレイヤー（`replay-embed.js`）がこのブロックを読んでアニメーションと実況ログを描画する。プレイヤーは英語の内部 ID（`Scizor`, `Volt Switch` など）で技データや画像を引くため、このブロックを日本語に置換するとプレイヤーが壊れる。

そのため、このツールは `battle-log-data` を **完全に保持** し、それ以外のテキスト（静的ログ・タイトル・h1）のみを翻訳する。結果：

- 上部のアニメーション再生部分 → 英語のまま（正常動作）
- 下部の静的テキストログ → 日本語

## ディレクトリ構成

```
showdown/
├── index.html          # 目次ページ
├── win/win-*.html      # 勝ち試合のリプレイ
├── lose/lose-*.html    # 負け試合のリプレイ
└── tools/
    ├── translate.py    # 翻訳スクリプト本体
    └── README.md       # このファイル
```

## 使い方

### 新しいリプレイを日本語化する

1. Pokemon Showdown でリプレイページを開き、HTML をダウンロードして `showdown/win/` または `showdown/lose/` に配置する（例: `win-8.html`）。
2. 以下を実行：

   ```bash
   python3 showdown/tools/translate.py
   ```

3. スクリプトは `../win/*.html` と `../lose/*.html` を自動検出し、すべて日本語化する。既に日本語化済みのファイルに再実行しても壊れない（冪等）。
4. `index.html` のリプレイ一覧にも手動でリンクを追加する（このスクリプトは `index.html` を触らない）。

### 特定のファイルだけ処理する

```bash
python3 showdown/tools/translate.py showdown/win/win-8.html
```

### やり直したくなったら

翻訳は in-place で書き換える。失敗したら git で戻せる：

```bash
git restore showdown/win/ showdown/lose/
```

## 翻訳辞書の拡張

新しいポケモン・技・特性・道具・メッセージが出てきて翻訳されない場合は、`translate.py` 内の該当テーブルに追記する。

### テーブルの役割

| テーブル | 対象 | 例 |
|---|---|---|
| `POKEMON` | ポケモン種族名、フォルム、メガ | `"Bellibolt": "ハラバリー"` |
| `MOVES` | 技名 | `"Volt Switch": "ボルトチェンジ"` |
| `ABILITIES` | 特性 | `"Intimidate": "いかく"` |
| `ITEMS` | 持ち物（メガストーン・きのみ等） | `"Leftovers": "たべのこし"` |
| `STATS` | 能力値ラベル | `"Sp. Atk": "とくこう"` |
| `PHRASES` | バトルログの定型文 | `"It's super effective!": "こうかは ばつぐんだ！"` |

### 追記する際の注意

1. **公式の日本語名を使う**。ポケモン徹底攻略 / Bulbapedia 日本版 / [ポケモン公式図鑑](https://zukan.pokemon.co.jp/) / Pokemon Wiki 等で必ず確認する。
2. **長いキー優先**。スクリプトは文字列長降順でマッチするので、`"Charizard-Mega-X"` と `"Charizard"` のような包含関係は自動で解決される。順序は気にしなくてよい（ただし重複キーは避ける）。
3. **`PHRASES` のキーは前後のスペースに注意**。`" fainted!"` のように先頭スペースを含めると「○○ fainted!」のような部分文字列にヒットする。スペースを含めないと `fainted` 単独で発火して誤置換になりうる。
4. **メガ進化や伏線フォルム**。`Charizard-Mega-X`（内部ID風）と `Mega Charizard`（ログ文言）の両方を登録する必要がある。既存エントリを参考にする。
5. **正規表現パターン**は `PRE_REGEX`（英語テキストを必要とする処理）と `POST_REGEX`（後処理）に分かれている。位置依存の整形（「X メガシンカした」など）は regex で書く。

### 未対応メッセージを素早く見つける方法

翻訳実行後、下記で残存英語を洗い出せる：

```bash
python3 -c "
import re
from pathlib import Path
seen = set()
for f in sorted(Path('showdown').rglob('*.html')):
    if f.name == 'index.html': continue
    content = f.read_text()
    m = re.search(r'<div class=\"battle-log battle-log-inline\">(.*)</div></div>\s*</div>', content, re.DOTALL)
    if not m: continue
    text = re.sub(r'<[^>]+>', ' ', m.group(1))
    for match in re.finditer(r'([A-Z][a-z]+|[a-z]{3,})(?:\s+([A-Z][a-z]+|[a-z]{3,})){1,8}', text):
        seen.add(match.group(0))
for p in sorted(seen):
    print(p)
"
```

プレイヤー名、フォーマット名（`Gen 9 Champions` など）はそのまま残るが、それ以外の英語フレーズが出てくる場合は翻訳辞書に追記が必要。

## 動作確認

ブラウザで開いて目視確認するのが確実：

```bash
# 作業ディレクトリを public_html の親にして
python3 -m http.server 8765
# → http://localhost:8765/showdown/win/win-1.html を開く
```

- 上部のアニメーション再生が動作すること
- 下部の静的ログが日本語になっていること
- タイトルが「○○ リプレイ: プレイヤー名 vs. プレイヤー名」になっていること

## 既知の制限

- **再生プレイヤー内の実況ログ**（動画と同期して流れる方）は英語のまま。これは `replay-embed.js` が `battle-log-data` から動的生成するため日本語化できない。
- フォーマット名（`[Gen 9 Champions] BSS Reg M-A` など）は意図的に英語のまま残している。変更したい場合は `PRE_REGEX` のタイトルパターンを編集する。
- プレイヤー名は置換しない。`"quechon"`, `"gabegabe12"` 等はそのまま表示される。
- 稀に「！」と「!」が混在する。機能上問題ないが気になる場合は最後に一括置換できる。

## ライセンス / 帰属

- 翻訳表は任天堂／ゲームフリーク公式のポケモン日本語名および本編ゲームのメッセージ文言に準拠する。
- スクリプト自体はこのプロジェクト固有の内部ツール。外部共有時はポケモン商標に留意すること。
