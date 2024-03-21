import os

def BuildGigaReq(url, range, file, **headers):
  headers = [f"-H '{k}: {v}'" for (k,v) in headers.items()]
  expr = f"curl '{url}' -H 'range: bytes={range}-' {' '.join(headers)}"
  os.system(f'{expr} --compressed >> {file}')


def Request(url, file):
  file_size = 0
  while True:
    if os.path.exists(file):
      new_file_size = os.stat(file).st_size
      print(f'{new_file_size=}')
      if new_file_size == file_size:
        break

    BuildGigaReq(url, file_size, file, **{
      'authority': 'bdneftgehk.cfd',
      'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9',
      'dnt': 1,
      'referer': 'https://javquick.com/',
      'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
      'sec-ch-ua-mobile': '?0',
      'sec-cha-ua-platform': '"Linux"',
      'sec-fetch-dest': 'video',
      'sec-fetch-mode': 'no-cors',
      'sec-fetch-site': 'cross-site',
      'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })

Request('https://bdneftgehk.cfd/serve/gd2/NDXwqlz7flngWQiY9VHsLvZSCwHaMFIAQTNU94LsTidS76wyKJKRdn8sn3nus3mHoUkQYlIGkty_M7kvYC2fG01MLTVXdQf06XxqarRHrmvOR9LX1ohwGQaaY5CW-819ibrcS10z3Z68WIMoRGp3TxHXzuG65lCki9QmbdGzUjMKsRW0rs1j34SuqIOtLTrvn58uXoYtOKgktQE_leSOSp5SX71z9om9bwoVCux9QBTCVO_D06KzWB4VwG0BmHoPFyk2YG3NAJELUExAi9e6UQWD5ua2LfXjxs4M-1wb85rPJD53GBBAwNtj3khfgJ1tWcfIYLzue-GG5GdzXFCN7t7UXDDIihcgASUYnDwPkOHWuqkUA7PnOCkYI6l4pHwKI7Tqowpog13h51oicmlUi67N8GLfW89qJG9faem1k7ESBNgK9O4c6c-cIeo4bxo4zFXxnFSVlrYU3QiEwMalDyles0IO1EB87Gi6T-1LMUg=.mp4',
        'aqua009.mp4')