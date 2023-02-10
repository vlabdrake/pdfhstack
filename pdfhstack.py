import argparse
from pathlib import Path
from io import BytesIO
from typing import IO

try:
    from pypdf import PageObject, PdfReader, PdfWriter
except ImportError as e:
    if __name__ == "__main__":
        print("pdfhstack requires pypdf to work. Install it first")
        exit(1)
    else:
        raise e


def hstack(files: [str | IO | Path]) -> BytesIO:
    pages = []
    for f in files:
        pages += PdfReader(f).pages

    pages.sort(key=lambda page: page.cropbox.height)

    width = sum(page.cropbox.width for page in pages)
    height = max(page.cropbox.height for page in pages)

    out = PageObject.create_blank_page(width=width, height=height)

    current_x = 0
    for page in pages:
        out.merge_translated_page(
            page, tx=current_x, ty=out.cropbox.height - page.cropbox.height
        )
        current_x += page.cropbox.width

    writer = PdfWriter()
    writer.add_page(out)

    output = BytesIO()
    writer.write(output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pdfhstack", description="Merge pages of pdf documents horizontally"
    )
    parser.add_argument("files", nargs="+", type=Path, help="files to merge")
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="out.pdf",
        type=Path,
        help="output file",
    )
    args = parser.parse_args()

    args.output.write_bytes(hstack(args.files).getbuffer())
