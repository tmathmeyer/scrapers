
from html.parser import HTMLParser
import requests

from impulse.util import typecheck


VOID_TAGS = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'keygen', 'link', 'menuitem', 'meta', 'param', 'source', 'track',
             'wbr']


class HTMLParserBase(HTMLParser):

  @typecheck.Ensure
  def url(self, url:str):
    content = str(requests.get(url).content.decode('utf-8'))
    return self.feed(content)

  @typecheck.Ensure
  def file(self, file:str):
    with open(file, 'r') as f:
      return self.feed(f.read())

  @typecheck.Ensure
  def feed(self, content:str):
    self._reset()
    super().feed(content)
    return self._content()

  @typecheck.Ensure
  def _reset(self):
    raise NotImplementedError()

  @typecheck.Ensure
  def _content(self):
    raise NotImplementedError()

  @typecheck.Ensure
  def handleStartTag(self, tag:str, attrs:dict):
    raise NotImplementedError()

  @typecheck.Ensure
  def handleEndTag(self, tag:str):
    raise NotImplementedError()

  @typecheck.Ensure
  def handleData(self, data:str):
    raise NotImplementedError()

  @typecheck.Ensure
  def handle_starttag(self, tag, attrs):
    self.handleStartTag(tag, dict(attrs))

  @typecheck.Ensure
  def handle_endtag(self, tag):
    self.handleEndTag(tag)

  @typecheck.Ensure
  def handle_data(self, data):
    self.handleData(data)


class XMLTag():
  __slots__ = ('_parent', '_tag', '_attrs', '_closed', '_children')

  def __init__(self, parent, tag, attrs, closed=False):
    self._parent = parent
    self._tag = tag
    self._attrs = attrs
    self._closed = closed
    self._children = []

  @typecheck.Ensure
  def Tag(self) -> str:
    return self._tag

  @typecheck.Ensure
  def Up(self) -> 'XMLTag':
    return self._parent

  @typecheck.Ensure
  def Top(self):
    if self._parent is None:
      return self
    return self._parent.Top()

  @typecheck.Ensure
  def Attr(self, attr:str, *args):
    return self._attrs.get(attr, *args)

  @typecheck.Ensure
  def Children(self):
    yield from self._children

  def ChildCount(self):
    return len(self._children)

  @typecheck.Ensure
  def LastChild(self):
    return self._children[-1] if self._children else None

  @typecheck.Ensure
  def FirstChild(self):
    return self._children[0] if self._children else None

  @typecheck.Ensure
  def RemoveLastChild(self):
    self._children = self._children[:-1]

  def _Content(self):
    for child in self.Children():
      if type(child) == XMLTag:
        yield from child.Content()
      else:
        yield child

  def Content(self):
    return ''.join(self._Content())

  @typecheck.Ensure
  def Select(self, tag=None, **attrs):
    if '_clazz' in attrs and 'class' not in attrs:
      attrs['class'] = attrs['_clazz']
      del attrs['_clazz']
    if self._matches(tag, attrs):
      yield self
    for child in self.Children():
      if type(child) == XMLTag:
        yield from child.Select(tag, **attrs)

  @typecheck.Ensure
  def SelectDirect(self, tag=None, **attrs):
    if '_clazz' in attrs and 'class' not in attrs:
      attrs['class'] = attrs['_clazz']
      del attrs['_clazz']
    if self._matches(tag, attrs):
      yield self
    for child in self.Children():
      if type(child) == XMLTag:
        if child._matches(tag, attrs):
          yield child


  @typecheck.Ensure
  def _matches(self, tag, attrs):
    if tag != self._tag:
      return False
    for k,v in attrs.items():
      if k not in self._attrs:
        return False
      if type(v) == str:
        if v != self._attrs[k]:
          return False
      elif not v.matches(self._attrs[k]):
        return False
    return True

  @typecheck.Ensure
  def Close(self):
    self._closed = True

  @typecheck.Ensure
  def AppendChild(self, tag:'XMLTag'):
    self._children.append(tag)

  @typecheck.Ensure
  def AppendData(self, data:str):
    self._children.append(data)

  def __repr__(self):
    return f'<{self._tag} .../>'

  def PrettyPrint(self, indent=0):
    attrs = ' '.join([f'{k}="{v}"' for k,v in self._attrs.items()])
    print(f'{" "*indent}<{self._tag} {attrs}>')
    for sub in self.Children():
      if type(sub) is not str:
        sub.PrettyPrint(indent+1)
      else:
        print(f'{" "*(indent+1)}{sub}')
    print(f'{" "*indent}</{self._tag}>')


class ExtractorTreeParser(HTMLParserBase):
  def __init__(self, tag:str):
    super().__init__()
    self._tags:[XMLTag] = []
    self._tag:str = tag
    self._current:XMLTag = None

  def _reset(self):
    self._tags = []

  @typecheck.Ensure
  def _content(self):
    return self._tags

  @typecheck.Ensure
  def handleStartTag(self, tag:str, attrs:dict):
    if tag != self._tag and self._current is None:
      return
    if self._current is not None:
      child = XMLTag(self._current, tag, attrs)
      self._current.AppendChild(child)
      if tag not in VOID_TAGS:
        self._current = child
      return
    assert self._current is None
    assert tag == self._tag
    self._current = XMLTag(None, tag, attrs)

  @typecheck.Ensure
  def handleEndTag(self, tag:str):
    if self._current is None:
      return
    if self._current.Tag() != tag:
      print(self._current.Top().PrettyPrint())
      raise ValueError(f'tried to close <{tag}> on <{self._current}>')
    self._current.Close()
    up = self._current.Up()
    if up is None:
      self._tags.append(self._current)
    self._current = up

  @typecheck.Ensure
  def handleData(self, data:str):
    data = data.strip()
    if self._current is not None:
      self._current.AppendData(data)


class XMLTreeParser(HTMLParserBase):
  def __init__(self, strict=False, test_invalid_html=None):
    super().__init__()
    self._tag = None
    self._strict = strict
    self._allowVoid = ''
    self._isKnownToBeMissingClose = test_invalid_html or (lambda *_: False)

  def _reset(self):
    self._tag = None

  @typecheck.Ensure
  def _content(self):
    return self._tag

  @typecheck.Ensure
  def handleStartTag(self, tag:str, attrs:dict):
    if self._isKnownToBeMissingClose(tag, attrs):
      self.handleEndTag(self._tag._tag)
    newtag = XMLTag(self._tag, tag, attrs)
    self._allowVoid = ''
    if tag in VOID_TAGS:
      self._allowVoid = tag
    if self._tag:
      self._tag.AppendChild(newtag)
    if not self._allowVoid:
      # Don't jump down a level for void tags!
      self._tag = newtag

  @typecheck.Ensure
  def handleEndTag(self, tag:str):
    void, self._allowVoid = self._allowVoid, ''
    if void:
      if tag == void:
        # we got a /> at the end of a void tag. this is allowed.
        # don't jump up, just unset the allowed.
        return
    if self._tag._tag != tag:
      # A rare case, could be a <...> instead of a </...>
      if self._tag.Up() and self._tag._tag == self._tag.Up()._tag:
        if self._tag.Up().Up() and self._tag.Up().Up()._tag == tag:
          self._tag.Up().RemoveLastChild()
          self._tag.Up().Close()
          self._tag.Up().Up().Close()
          parent = self._tag.Up().Up().Up()
          if parent is not None:
            self._tag = parent
          return
      if self._strict:
        raise ValueError(f'unexpected </{tag}>, wanted </{self._tag._tag}>')
      else:
        return
    parent = self._tag.Up()
    self._tag.Close()
    if parent is not None:
      self._tag = parent

  @typecheck.Ensure
  def handleData(self, data:str):
    data = data.strip()
    if data:
      if not self._tag:
        print(f'trying to append, but its not allowed! {self._tag} {data}')
      self._tag.AppendData(data)