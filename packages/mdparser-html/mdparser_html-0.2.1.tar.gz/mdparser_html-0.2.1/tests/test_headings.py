
from mdparser.core import parse_markdown

def test_h1():
    html = parse_markdown("# Hello")
    assert "<h1>Hello</h1>" in html

def test_h3():
    html = parse_markdown("### Title")
    assert "<h3>Title</h3>" in html

def test_h8():
    html = parse_markdown("######## Deep")
    assert "<h8>Deep</h8>" in html
