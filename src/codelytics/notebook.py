import pathlib

import nbformat


class Notebook:
    """
    Analyze Jupyter Notebook files.

    Provides functionality to extract and analyze content from Jupyter notebooks,
    including code cells, markdown cells, and cell counting.

    Parameters
    ----------
    path : pathlib.Path or str
        Path to the Jupyter notebook file (.ipynb).

    Attributes
    ----------
    path : pathlib.Path
        Path to the notebook file.
    nb : nbformat.NotebookNode
        Parsed notebook object.
    """

    def __init__(self, path):
        if isinstance(path, str):
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
        separated by double newlines.

        Parameters
        ----------
        cell_type : str
            Type of cells to extract. Options are:
            - 'code': Extract code cells
            - 'markdown': Extract markdown cells
            - 'raw': Extract raw cells

        Returns
        -------
        str
            All cells of specified type merged together as a single string.
            Returns empty string if no cells of the specified type found.
        """
        return "\n\n".join(
            [
                cell.source
                for cell in self.nb.cells
                if cell.cell_type == cell_type and cell.source.strip()
            ]
        )
