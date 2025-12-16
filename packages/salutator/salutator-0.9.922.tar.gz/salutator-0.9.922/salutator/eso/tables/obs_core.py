import sys
import pandas as pd
from typing import List
from pyvo.dal import TAPService
from .eso_table import EsoTable, EsoColumn
from .namespace import TableNames, TAP_URL


class EsoIndexer():  # to return stuff
    def __init__(self, table_name, maxlen, required_columns):
        self.maxlen = maxlen
        self.table_name = table_name
        self.required_columns = required_columns
        self._top = 0
        self._data = pd.DataFrame()

    def __getitem__(self, index):
        # 1. Chose behaviour depending on key type.
        if isinstance(index, slice):
            start = 0 if index.start is None else index.start
            stop = self.maxlen if index.stop is None else index.stop
            top = max(start, stop)
        elif isinstance(index, int):
            top = index+1
        elif isinstance(index, list):
            top = len(index)
        else:
            top = 0

        # 2. Get the data if needed.
        if top > self._top:
            self._top = top
            self._data = TAPService(TAP_URL).search(
                query=(f"select top {self._top} {', '.join(self.required_columns)} "
                       f"from {self.table_name} order by {self.required_columns[0]}"),
                maxrec=sys.maxsize,
            ).to_table().to_pandas()
        return self._data.iloc[index]


class ObsCoreColumn(EsoColumn):
    """
    ObsCore column
    """
    parent_table_name = TableNames.observations

    def __init__(self, column_name):
        self.name = column_name
        self._top = 0
        self._series = pd.Series()

    def __getitem__(self, key):
        # 1. Chose behaviour depending on key type.
        if isinstance(key, slice):
            start = 0 if key.start is None else key.start
            stop = self.__len__() if key.stop is None else key.stop
            self._top = max(start, stop)
        else:
            if key > self.__len__() - 1:
                raise IndexError(f"Index {key} out of bounds. Max allowed: {self.__len__()-1}")
            self._top = key+1

        # 2. Get the data if needed.
        if self._series.empty or self._top > len(self._series):
            self._series = TAPService(TAP_URL).search(
                query=f"select top {self._top} {self.name} from {self.parent_table_name} order by {self.name}",
                maxrec=sys.maxsize,
            ).to_table().to_pandas()[self.name]
        return self._series[key]

    def __len__(self):
        return TAPService(TAP_URL).search(
            query=f"select count(*) as q from {self.parent_table_name}"
        ).to_table().to_pandas()["q"][0]

    def __lt__(self, other):
        return (self._series < other)

    def __le__(self, other):
        return (self._series <= other)

    def __gt__(self, other):
        return (self._series > other)

    def __ge__(self, other):
        return (len(self._series) >= len(other))

    def __eq__(self, other):
        return (len(self._series) == len(other))

    def __ne__(self, other):
        return not (self.__eq__(other))


class ObsCoreTable(EsoTable):
    """
    ObsCore table
    """

    def __init__(self, required_columns: List[str] = None):
        self._table_name = TableNames.observations
        self._allowed_colnames = TAPService(TAP_URL).search(
            query=f"select top 0 * from {self._table_name}").to_table().colnames
        self._top = 0
        self._df = pd.DataFrame()

        self._colnames = required_columns or self._allowed_colnames[:]

        for key in self._colnames:
            self.__dict__[key] = ObsCoreColumn(key)

        self.iloc = EsoIndexer(self._table_name, self.__len__(), self._colnames)

    @property
    def colnames(self):
        """
        The column names
        """
        return self._colnames

    @colnames.setter
    def colnames(self, value):
        raise ValueError("Property cannot be modified by user")

    def __getitem__(self, key):
        retval = None

        # Option 2: returns an EsoTable of ObsCore Columns
        if isinstance(key, list):
            required_columns = []
            for k in key:
                if k not in self._colnames:
                    raise KeyError(f"{k} is not a column name")
                required_columns.append(k)
            retval = ObsCoreTable(required_columns=required_columns)

        # Option 1: Returns an ObsCoreColumn
        elif isinstance(key, str):
            retval = self.__dict__[key]  # An ObsCoreColumn

        else:
            raise KeyError(f"{key} is not a valid key. Valid keys are str or List[str]")

        return retval

    def __len__(self):
        return TAPService(TAP_URL).search(
            query=f"select count(*) as q from {self._table_name}"
        ).to_table().to_pandas()["q"][0]
