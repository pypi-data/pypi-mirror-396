from mdparser.core import parse_markdown

def test_paragraph_wrap():
    html = parse_markdown("Hello world")
    assert "<p>Hello world</p>" in html

def test_no_paragraph_inside_heading():
    html = parse_markdown("# Title")
    assert "<p>" not in html.split("</h1>")[0]

