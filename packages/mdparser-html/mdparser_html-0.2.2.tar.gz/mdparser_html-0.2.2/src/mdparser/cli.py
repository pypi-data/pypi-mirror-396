import argparse


from mdparser.core import parse_markdown



def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML.")
    parser.add_argument("input", help="Path to the input Markdown file.")
    parser.add_argument("-o","--output", help="Path to the output HTML file.")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as infile:
        markdown_text = infile.read()

    html_text = parse_markdown(markdown_text)

    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(html_text)

    print(f"Converted {args.input} to {args.output}")


