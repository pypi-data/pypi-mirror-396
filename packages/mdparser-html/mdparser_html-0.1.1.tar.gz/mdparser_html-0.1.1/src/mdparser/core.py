import re

# -------------------------------
# BLOCK: HEADINGS
# -------------------------------
def parse_headings(text):
    text = re.sub(r'######## (.*)', r'<h8>\1</h8>', text)
    text = re.sub(r'####### (.*)', r'<h7>\1</h7>', text)
    text = re.sub(r'###### (.*)', r'<h6>\1</h6>', text)
    text = re.sub(r'##### (.*)', r'<h5>\1</h5>', text)
    text = re.sub(r'#### (.*)', r'<h4>\1</h4>', text)
    text = re.sub(r'### (.*)', r'<h3>\1</h3>', text)
    text = re.sub(r'## (.*)', r'<h2>\1</h2>', text)
    text = re.sub(r'# (.*)', r'<h1>\1</h1>', text)
    return text


# -------------------------------
# INLINE: BOLD, ITALIC, CODE
# -------------------------------
def parse_inline(text):
    # bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    # italic: *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

    # italic: _text_
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)

    # inline code
    text = re.sub(r'`([^`]*)`', r'<code>\1</code>', text)

    return text


# -------------------------------
# LISTS: UL + OL
# -------------------------------
def unorderedList(match):
    items = match.group(0).strip().split("\n")
    list_items = "".join([f"<li>{item[2:].strip()}</li>\n" for item in items])
    return f"<ul>\n{list_items}</ul>"

def orderedList(match):
    items = match.group(0).strip().split("\n")
    list_items = ""
    for item in items:
        _, text = item.split(". ", 1)
        list_items += f"<li>{text.strip()}</li>\n"
    return f"<ol>\n{list_items}</ol>"

def parse_lists(text):
    text = re.sub(r'(^- .+(?:\n- .+)*)', unorderedList, text, flags=re.MULTILINE)
    text = re.sub(r'(^\d+\. .+(?:\n\d+\. .+)*)', orderedList, text, flags=re.MULTILINE)
    return text


# -------------------------------
# FENCED DIVS (RECURSIVE)
# -------------------------------
def fenced_div(match):
    class_name = match.group(1)
    inner_markdown = match.group(2).strip()

    # recursive parse!
    inner_html = parse_markdown(inner_markdown)

    return f'<div class="{class_name}">\n{inner_html}\n</div>'

def parse_fenced_divs(text):
    return re.sub(
        r':::\s*(\w+)\s*\n(.*?)\n:::\s*',
        fenced_div,
        text,
        flags=re.S
    )


# -------------------------------
# PARAGRAPHS
# -------------------------------
def wrap_paragraphs(html):
    lines = html.split("\n")
    result = []
    in_pre_block = False
    for line in lines:
        stripped = line.strip()

        if not stripped:
            result.append("")
            continue
                # detect start of code block
        if stripped.startswith("<pre>") or stripped.startswith("<pre "):
            in_pre_block = True
            result.append(line)
            continue

        # detect end of code block
        if stripped.startswith("</pre>"):
            in_pre_block = False
            result.append(line)
            continue

        # if inside <pre>...</pre> → do NOT wrap
        if in_pre_block:
            result.append(line)
            continue

        if (stripped.startswith("<h") and stripped.endswith(">")) \
           or stripped.startswith("<ol>") or stripped.startswith("<ul>") \
           or stripped.startswith("</ol>") or stripped.startswith("</ul>") \
           or stripped.startswith("<li>") \
           or stripped.startswith("<pre>") or stripped.startswith("</pre>") \
           or stripped.startswith("<code>") or stripped.startswith("</code>") \
           or (stripped.startswith("<") and stripped.endswith(">")) \
          or stripped.startswith("</div>") or stripped.startswith("<div") :
            result.append(line)
            continue

        result.append(f"<p>{stripped}</p>")

    return "\n".join(result)



# -------------------------------
# CODE BLOCKS
# -------------------------------

def normalize_language(lang):
    if not lang or len(lang) <= 1:
        return "bash"
    return lang.lower()

def code_block(match):
    language = match.group(1)
    code_content = match.group(2)
    newLanguage = normalize_language(language)
    code_content = ( code_content.replace("&", "&amp;") .replace("<", "&lt;") .replace(">", "&gt;") )
    return f'<pre><code class="language-{newLanguage}">\n{code_content}\n</code></pre>'

def parse_code(text):
    return re.sub(r'```(\w*)\s*\n(.*?)\n```',code_block, text, flags=re.S)






# -------------------------------
# images
# -------------------------------

def parse_image(match):
    alt_text = match.group(1)
    url = match.group(2)
    title = match.group(3)

    title_attr = f' title="{title}"' if title else ''
    return f'<img src="{url}" alt="{alt_text}"{title_attr} />'

def parse_images(text):
    return re.sub(
        r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)',
        parse_image,
        text
    )





# -------------------------------
# MAIN PIPELINE
# -------------------------------
def parse_markdown(text):
    text = parse_fenced_divs(text)
    text = parse_code(text)          # MUST BE FIRST!!
    text = parse_headings(text)
    text = parse_lists(text)
    text = parse_inline(text)
    text = parse_images(text)
    text = wrap_paragraphs(text)
    return text





# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    with open("test.md") as f:
        content = f.read()
    html = '''
<html>
<head>
    <title>Markdown to HTML</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>

</head>
<body>

'''
    html += parse_markdown(content)
    html += '''
</body>
</html>
'''
    with open("output.html", "w") as f:
        f.write(html)

    print("Converted!")

