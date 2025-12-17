# mdparser-html

A lightweight, extensible **Markdown → HTML** converter with a clean Python API and CLI.

Built for simplicity, hackability, and future extension.

---

## 🤔 Why mdparser-html?

- Lightweight alternative to full Markdown engines
- Easy to extend and hack
- Designed for learning, tooling, and static generators

## ✨ Features

- Markdown → HTML conversion
- Full HTML document or body-only output
- Syntax highlighting via CDN (Prism / Highlight.js)
- Headings, lists, code blocks, images
- Fenced blocks (`:::`)
- CLI + Python API
- Zero runtime dependencies

---

## 📦 Installation

```bash
pip install mdparser-html
```

## 🚀 Usage CLI

```bash
md2html input.md -o output.html
```

## </> Python API

Basic usage

```python
from mdparser import parse_markdown

html = parse_markdown("# Hello World")
print(html)
```

## ⚙️ Configuration Options

# Advanced usage

```python
html = parse_markdown(
    markdown_text,
    full_html=True,
    title="My Document",
    include_cdn=True  # Include syntax highlighting CDN links
)
print(html)
```

# Body-only output

```python
body = parse_markdown(markdown_text, full_html=False)
print(body)
```

## Fenced blocks

```md
:::

# Welcome

This is a hero section
:::
```

# rendered as

```html
<div class="hero">
  <h1>Welcome</h1>
  <p>This is a hero section</p>
</div>
```

## 🗂️ Supported Markdown

- Headings (`#` → `########`)
- Bold / Italic
- Inline code
- Fenced code blocks
- Ordered & unordered lists
- Images
- Fenced div blocks

## 🛠 Design Notes

- Single public API: `parse_markdown`
- Internal helpers are intentionally hidden
- Designed for future renderers (HTML today, more later)

## 🧾 CHANGELOG.md

Create a new file called **`CHANGELOG.md`**

## 🗺 Roadmap

- AST-based parser
- Performance optimizations
- Additional output formats (e.g. Pug)
- Plugin hooks

## 🤝 Contributing

Pull requests are welcome.  
Please open an issue before major changes.

## License

MIT License © 2025 Tarun Nayaka R (Rtarun3606k)
