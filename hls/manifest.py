
import os
import requests
import typing


class Playlist():
  def SetUrl(self, webdir, manifest):
    self.webdir = webdir
    self.uri = f'{webdir}/{manifest}'


class MultivariantPlaylist(Playlist):
  def __init__(self, manifest):
    super().__init__()
    self.manifests = manifest

  def Download(self, directory:str):
    for manifest in self.manifests:
      dirz, file = os.path.split(manifest)
      assert file.endswith('.m3u8')
      writedir = directory
      if dirz:
        writedir = os.path.join(writedir, dirz)
        if not os.path.exists(writedir):
          os.makedirs(writedir)
      FetchManifest(f'{self.webdir}/{manifest}', writedir)


class MediaPlaylist(Playlist):
  def __init__(self, segments):
    super().__init__()
    self.segments = segments

  def Download(self, directory:str):
    for segment in self.segments:
      dirz, file = os.path.split(segment)
      writedir = directory
      if dirz:
        writedir = os.path.join(writedir, dirz)
        if not os.path.exists(writedir):
          os.makedirs(writedir)
      if not os.path.exists(f'{writedir}/{file}'):
        os.system(f'curl {self.webdir}/{segment} -o {writedir}/{file}')


def FetchManifest(url:str, directory:str):
  while not url.endswith('.m3u8'):
    url = url[:-1]

  webdir, manifest = url.rsplit('/', 1)
  fetch = requests.get(url)
  content = fetch.text

  playlist = ParsePlaylist(content)
  playlist.SetUrl(webdir, manifest)

  if not os.path.exists(directory):
    os.makedirs(directory)
  with open(os.path.join(directory, manifest), 'w+') as f:
    f.write(content)

  playlist.Download(directory)


def ParsePlaylist(content:str) -> Playlist:
  lines = iter(content.split('\n'))
  assert next(lines) == '#EXTM3U'
  for line in lines:
    if line.startswith('#EXT-X-MAP'):
      return ParseMediaPlaylist(line, lines)
    if line.startswith('#EXTINF'):
      return ParseMediaPlaylist(line, lines)
    if line.startswith('#EXT-X-STREAM-INF'):
      return ParseMultivariantPlaylist(line, lines)
    if line.startswith('#EXT-X-MEDIA:'):
      return ParseMultivariantPlaylist(line, lines)
  raise ValueError('invalid playlist')


def ParseMediaPlaylist(line:str, lines:typing.Iterator[str]) -> MediaPlaylist:
  files = set()
  if line.startswith('#EXT-X-MAP'):
    files.add(line.split('"')[1])
  has_parsed_inf = line.startswith('#EXTINF')
  for line in lines:
    if has_parsed_inf and line[0] != '#':
      has_parsed_inf = False
      files.add(line)
    elif line.startswith('#EXTINF:'):
      has_parsed_inf = True
  return MediaPlaylist(files)


def ParseMultivariantPlaylist(line:str, lines:[str]) -> MultivariantPlaylist:
  manifests = ParseMultivariantLine(line)
  for line in lines:
    manifests += ParseMultivariantLine(line)
  return MultivariantPlaylist(manifests)


def ParseMultivariantLine(line:str) -> [str]:
  if not len(line):
    return []
  if line.startswith('#EXT-X-MEDIA'):
    if 'URI=' not in line:
      return []
    pre, post, *_ = line.split('URI="')
    assert len(_) == 0
    pre, *_ = post.split('",')
    return [pre[:-1]]
  if line[0] != '#' and line.endswith('.m3u8'):
    return [line]
  return []


FetchManifest("https://devstreaming-cdn.apple.com/videos/streaming/examples/adv_dv_atmos/main.m3u8", "atmos")
