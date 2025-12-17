"""Parallel processing utilities."""

from typing import Any, Callable, List

from joblib import Parallel, delayed


def parallel_process(
    func: Callable, items: List[Any], n_jobs: int = -1, desc: str = "Processing"
) -> List[Any]:
    """
    Process items in parallel using joblib.

    Parameters
    ----------
    func : Callable
        Function to apply to each item
    items : List
        Items to process
    n_jobs : int
        Number of parallel jobs (-1 = all cores)
    desc : str
        Description for progress bar

    Returns
    -------
    List
        Results from processing each item
    """
    return Parallel(n_jobs=n_jobs)(delayed(func)(item) for item in items)


class ParallelProcessor:
    """
    Parallel processor for batch EEG analysis.

    Parameters
    ----------
    n_jobs : int, default=-1
        Number of parallel jobs. -1 means using all processors.
    backend : str, default='loky'
        Joblib backend ('loky', 'threading', 'multiprocessing').
    verbose : int, default=0
        Verbosity level.

    Examples
    --------
    >>> processor = ParallelProcessor(n_jobs=4)
    >>> results = processor.map(process_func, data_list)
    """

    def __init__(self, n_jobs: int = -1, backend: str = "loky", verbose: int = 0):
        """Initialize parallel processor."""
        self.n_jobs = n_jobs
        self.backend = backend
        self.verbose = verbose

    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        Apply function to items in parallel.

        Parameters
        ----------
        func : Callable
            Function to apply
        items : List[Any]
            Items to process

        Returns
        -------
        List[Any]
            Results
        """
        return Parallel(n_jobs=self.n_jobs, backend=self.backend, verbose=self.verbose)(
            delayed(func)(item) for item in items
        )

    def process(self, func: Callable, items: List[Any]) -> List[Any]:
        """Alias for map method."""
        return self.map(func, items)
