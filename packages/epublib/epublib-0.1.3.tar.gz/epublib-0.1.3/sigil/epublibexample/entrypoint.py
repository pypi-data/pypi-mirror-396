import sys
from pathlib import Path

from epublib import EPUB


def process_book(book: EPUB) -> None:
    print(book.container_file.filename)
    book.metadata.title = "This book was transformed using EPUBLib!"


def main():
    book_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])

    book = EPUB(book_dir)
    process_book(book)
    book.write_to_folder(out_dir)


if __name__ == "__main__":
    main()
