
from impulse.util import typecheck
from scrapers.base import html


class RowType():
  class RowCount():
    def __init__(self, rowtype, count):
      self._rowtype = rowtype
      self._count = count

    def ParseRow(self, row):
      parsed = self._rowtype.ParseRow(row)
      self._count -= 1
      return parsed, self._count

    def __repr__(self):
      return str(self)

    def __str__(self):
      return f'<{self._count} * {self._rowtype}>'

  @typecheck.Ensure
  def __mul__(self, count:int):
    return RowType.RowCount(self, count)

  def ParseRow(self, row):
    raise NotImplementedError()

  def __repr__(self):
    return str(self)

  def __str__(self):
    return self.__class__.__name__


class TagRow(RowType):
  def __init__(self, tag, **kwargs):
    self._tag = tag
    self._attrs = kwargs
  def ParseRow(self, row):
    return list(row.SelectDirect(tag=self._tag, **self._attrs))


class KeyValueRow(RowType):
  def ParseRow(self, row):
    cells = list(row.SelectDirect(tag='td'))
    assert len(cells) == 2
    return cells[0].Content(), cells[1].Content()


class DropRow(RowType):
  def ParseRow(self, row):
    return None


class WholeRow(RowType):
  def ParseRow(self, row):
    return row


class ContentRow(RowType):
  def ParseRow(self, row):
    return row.Content()


class TableContent():
  def __init__(self, *rowcounts):
    self._rowcounts = list(rowcounts)

  def From(self, tabletag:html.XMLTag, lazy=False) -> ([None], int):
    parsed_rows = []
    for row in tabletag.SelectDirect('tr'):
      if not self._rowcounts:
        raise ValueError('exhausted expected rows!')
      parsed, remaining = self._rowcounts[0].ParseRow(row)
      if remaining == 0:
        self._rowcounts.pop(0)
      if parsed:
        parsed_rows.append(parsed)

    if self._rowcounts:
      if lazy:
        return parsed_rows, len(self._rowcounts)
      raise ValueError('exhausted available rows!')

    return parsed_rows, 0

  def __repr__(self):
    return str(self)

  def __str__(self):
    return f'Parser{self._rowcounts}'