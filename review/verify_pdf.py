"""Check the original and downloaded PDF from the ArtCraft acceptance run."""

from pathlib import Path

from pypdf import PdfReader


def read_sample(name):
    path = Path(__file__).resolve().parents[1] / "evidence" / "samples" / name
    reader = PdfReader(path)
    if len(reader.pages) != 1:
        raise ValueError(f"{name} should have exactly one page")
    page = reader.pages[0]
    return page.rotation, page.extract_text().strip()


def main():
    before = read_sample("pdfcraft-original.pdf")
    after = read_sample("pdfcraft-edited.pdf")
    if before != (0, "Original studio note") or after != (90, before[1]):
        raise SystemExit("The PDF rotation or text does not match the acceptance result")
    print("Verified: the page rotated from 0° to 90° and retained its original text.")


if __name__ == "__main__":
    main()
