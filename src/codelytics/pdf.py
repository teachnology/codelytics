import pathlib
import re

import fitz  # PyMuPDF


class PDF:
    """A class for reading and analysing PDF files.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the PDF file to be processed.

    Raises
    ------
    FileNotFoundError
        If the specified PDF file does not exist.
    """

    def __init__(self, path):
        self.path = pathlib.Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.path}")

    def references_page(self):
        """
        Locate the *last* page on which a references section heading appears.

        The PDF is scanned from the final page toward the first.  As soon as a
        stand-alone heading such as “References”, “Bibliography”, “Works Cited”,
        etc. is found, that page number is returned.

        Returns
        -------
        int or None
            1-indexed page number where the *last* references heading occurs,
            or ``None`` if no heading is found.

        Raises
        ------
        RuntimeError
            For any other problem while reading the PDF.

        """
        # List of normalised reference section keywords
        keyword_pattern = "|".join(
            re.escape(term)
            for term in [
                "references",
                "reference",
                "referances",
                "bibliography",
                "works cited",
                "work cited",
                "literature cited",
                "sources",
                "citations",
            ]
        )

        # Final compiled regex:
        # - optional numbered prefix (1, 1.2, 1.2.3., etc.)
        # - optional whitespace between parts
        # - optional colon at the end
        pattern = re.compile(
            rf"^\s*(\d+(\.\d+)*\.?)?\s*({keyword_pattern})\s*:?\s*$", re.IGNORECASE
        )

        try:
            with fitz.open(self.path) as doc:
                # Iterate from the last page to the first.
                for page_idx in range(len(doc) - 1, -1, -1):
                    page_number = page_idx + 1  # convert to 1-indexed
                    text = doc.load_page(page_idx).get_text()
                    if not text:
                        continue

                    for line in text.splitlines():
                        if pattern.match(line.strip()):
                            return page_number

                # If no references section is found, return None.
                return None

        except Exception as exc:
            raise RuntimeError(f"Error processing PDF file: {exc}") from exc

    @property
    def n_pages(self):
        """
        Return the total number of pages in the PDF.

        Returns
        -------
        int
            Number of pages in the PDF.

        Raises
        ------
        RuntimeError
            For any problem while reading the PDF.
        """
        try:
            with fitz.open(self.path) as doc:
                return len(doc)
        except Exception as exc:
            raise RuntimeError(f"Error processing PDF file: {exc}") from exc

    def count_words(self, ignore_pages=None):
        """
        Count words, excluding specified pages.

        Parameters
        ----------
        ignore_pages : list of int or str, optional
            Pages to ignore (1-indexed). Specify exact page numbers (e.g., [1, 2]) and a
            string like '>7' to ignore all pages after page 7.

        Returns
        -------
        int
            Total number of words on non-ignored pages.

        Raises
        ------
        ValueError
            If `ignore_pages` contains invalid entries.
        RuntimeError
            For any other problem while reading the PDF.

        """
        ignore_set = set()
        if ignore_pages:
            for item in ignore_pages:
                if isinstance(item, int):
                    ignore_set.add(item)
                elif isinstance(item, str) and item.startswith(">"):
                    ignore_set.update(
                        [i for i in range(int(item[1:]) + 1, self.n_pages + 1)]
                    )
                else:
                    raise ValueError(f"Invalid ignore_pages entry: {item}")

        words = 0
        try:
            with fitz.open(self.path) as doc:
                for page_number, page in enumerate(doc, start=1):  # 1-indexed
                    if page_number in ignore_set:
                        continue

                    if text := page.get_text():
                        words += len(text.split())

            return words

        except Exception as exc:
            raise RuntimeError(f"Error processing PDF file: {exc}") from exc
