
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
  def Up(self) -> 'XMLTag':
    return self._parent

  @typecheck.Ensure
  def Attr(self, attr:str, *args):
    return self._attrs.get(attr, *args)

  @typecheck.Ensure
  def Children(self):
    yield from self._children

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
    if self._matches(tag, attrs):
      yield self
    for child in self.Children():
      if type(child) == XMLTag:
        yield from child.Select(tag, **attrs)

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


class XMLTreeParser(HTMLParserBase):
  def __init__(self, strict=False):
    super().__init__()
    self._tag = None
    self._strict = strict
    self._allowVoid = ''

  def _reset(self):
    self._tag = None

  @typecheck.Ensure
  def _content(self):
    return self._tag

  @typecheck.Ensure
  def handleStartTag(self, tag:str, attrs:dict):
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
      raise ValueError(f'unexpected </{self._tag._tag}>, wanted </{tag}>')
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