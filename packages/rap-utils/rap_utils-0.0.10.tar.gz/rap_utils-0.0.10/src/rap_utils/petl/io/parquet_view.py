import petl
import pyarrow.parquet as pq

class ParquetView(petl.Table):
    def __init__(self, filename, **kwargs):
        # assume that a is a numpy array
        self.table = pq.read_table(filename, **kwargs)
    def __iter__(self):
        pass
        # yield the header row
        header = tuple(self.table.column_names)
        yield header
        # yield the data rows
        for batch in self.table.to_batches():
            for row in zip(*batch.columns):
                yield tuple(c.as_py() for c in row)