# Security Policy

`ja-furigana-dict` は **データ専用 repo** (TOML 辞書 + ルール) で、 実行コードを含まない。
セキュリティ報告窓口は engine 側に集約している。

## 脆弱性を見つけたら

- **engine / lib / CLI 経路の脆弱性** (TOML loader / archive 展開 / HTTP server 等):
  → [`ja-furigana` の SECURITY.md](https://github.com/RyuuNeko1107/ja-furigana/blob/master/SECURITY.md)
  - GitHub Security Advisories: https://github.com/RyuuNeko1107/ja-furigana/security/advisories/new
  - Email fallback: mail@ryuuneko.com

## このリポジトリの責務範囲

### In scope (このリポジトリで対応)

- **データ汚染**: 不正な PR で意図しない読み (誤読 / 商標違反 / 公序良俗違反) が
  merge されかける場合 → [GitHub Issues](https://github.com/RyuuNeko1107/ja-furigana-dict/issues)
  または PR review で指摘
- **悪意ある TOML**: 制御文字 / Unicode bidi override / homoglyph で contributor を
  だますような entry の混入 → engine 側 `crate::sanitize` で load 時 reject される
  ため害は無いが、 PR の段階で気づいた場合は close + 通報

### Out of scope (engine 側の SECURITY.md へ)

- TOML parser / loader の脆弱性
- `furigana dict pull` の archive 展開・ SHA-256 検証経路
- HTTP server / authentication
- 依存ライブラリの RUSTSEC / GHSA

## 「この読みは間違ってる」 type の報告

セキュリティではなく **データの正しさ** の問題なので:

- [reading_request.yml テンプレ](https://github.com/RyuuNeko1107/ja-furigana-dict/issues/new?template=reading_request.yml) で issue
- 直接 PR で修正 (TOML 1 行差し替え)

の方が早い。 公開 issue / PR で OK (脆弱性扱いではない)。
