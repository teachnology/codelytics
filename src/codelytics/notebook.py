import pathlib

import nbformat


class Notebook:
    """
    Analyse Jupyter Notebook files.

    Provides functionality to extract and analyse content from Jupyter notebooks,
    including code cells, markdown cells, and cell counting.

    Parameters
    ----------
    path : pathlib.Path or str
        Path to the Jupyter notebook file (.ipynb).

    """

    def __init__(self, path):
        path = pathlib.Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Notebook file not found: {path}")

        if not path.suffix == ".ipynb":
            raise ValueError(f"File must have .ipynb extension: {path}")

        self.path = path

        try:
            with open(path, encoding="utf-8") as f:
                self.nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        except Exception as e:
            raise ValueError(f"Invalid notebook file format: {e}")

    def n_cells(self, cell_type=None):
        """
        Return the number of cells in the notebook.

        Parameters
        ----------
        cell_type : str, optional
            Type of cells to count. Options are:
            - None: Count all cells (default)
            - 'code': Count only code cells
            - 'markdown': Count only markdown cells
            - 'raw': Count only raw cells

        Returns
        -------
        int
            Number of cells of the specified type.
        """
        if cell_type is None:
            return len(self.nb.cells)

        return len([cell for cell in self.nb.cells if cell.cell_type == cell_type])

    def extract(self, cell_type):
        """
        Extract content from notebook cells of specified type.

        Merges all cells of the specified type into a single string,
        preserving the order of cells in the notebook. Each cell is
        separated by double newlines. For code cells, filters out cells
        with syntax errors.

        Parameters
        ----------
        cell_type : str
            Type of cells to extract. Options are:
            - 'code': Extract code cells (excludes cells with syntax errors)
            - 'markdown': Extract markdown cells

        Returns
        -------
        str or Py or TextAnalysis
            All cells of specified type merged together.
            - For 'code': Returns Py object with valid syntax cells only
            - For 'markdown': Returns TextAnalysis object
            Returns empty content if no valid cells of the specified type found.
        """
        if cell_type == "code":
            from codelytics import Py  # noqa: PLC0415

            valid_cells = []

            for cell in self.nb.cells:
                if cell.cell_type == cell_type and cell.source.strip():
                    # Check if this individual cell has valid syntax
                    try:
                        if Py(cell.source).is_valid_syntax:
                            valid_cells.append(cell.source)
                    except Exception:
                        # Skip cells that can't be processed at all
                        continue

            return Py("\n\n".join(valid_cells))

        elif cell_type == "markdown":
            from codelytics import TextAnalysis  # noqa: PLC0415

            content = "\n\n".join(
                [
                    cell.source
                    for cell in self.nb.cells
                    if cell.cell_type == cell_type and cell.source.strip()
                ]
            )
            return TextAnalysis([content])

        else:
            raise ValueError(f"Unsupported cell type: {cell_type}")
