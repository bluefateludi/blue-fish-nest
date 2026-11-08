"""Import the selected public gallery assets; run with Python, Pillow and BeautifulSoup."""
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ASSETS = SITE / 'assets' / 'imported'
BASE = 'https://xn--pssy23gqgbz2d718b.com'
SELECTION = {
    '开心': [137, 7, 11, 17, 18, 38, 61, 79, 83, 87],
    '委屈': [1, 2, 3, 5, 8, 14, 30, 37, 39, 40],
    '摸鱼': [15, 28, 34, 41, 43, 136, 50, 53, 60, 88],
    '贴贴': [45, 57, 64, 69, 70, 74, 91, 123, 104, 132],
    '干饭': [9, 52, 55, 63, 76, 77, 78, 81, 85, 148],
}


def fetch(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def save_image(url, filename, animated=False):
    path = ASSETS / filename
    content = path.read_bytes() if path.exists() else fetch(url)
    if filename.endswith('-preview.webp'):
        with Image.open(io.BytesIO(content)) as preview:
            preview.seek(0)
            still = ImageOps.contain(preview.convert('RGBA'), (480, 480))
        buffer = io.BytesIO()
        still.save(buffer, 'WEBP', quality=82, method=6)
        content = buffer.getvalue()
    with Image.open(io.BytesIO(content)) as img:
        width, height = img.size
        frames = getattr(img, 'n_frames', 1)
        if animated and frames < 2:
            raise ValueError(f'Expected animation: {url}')
        img.verify()
    path.write_bytes(content)
    return {'image': f'assets/imported/{filename}', 'width': width, 'height': height,
            'frames': frames, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}


def static_item(item):
    entry, mood = item
    url = entry['original']
    number = Path(urllib.parse.urlparse(url).path).stem
    title = {7: '嘿嘿，这题我可太会了', 17: '小鱼和伙伴', 63: '小鱼影院', 76: '我是吃白饭的蓝色大肥鱼', 123: '我能去你家吃饭吗，就一碗', 136: '摸鱼事故簿', 137: '周五周五，敲锣打鼓', 148: '吃白饭的蓝色大肥鱼'}.get(int(number), entry['name'])
    quote = re.search('『(.*?)』', title)
    return {
        'id': f'gengjing-{number}', 'title': quote.group(1) if quote else title,
        'alt': title, 'mood': mood, 'desc': f'{mood}时刻的小鱼，今天用这张表达心情。',
        'tags': [mood, 'DeepSeek娘', '大肥鱼', '梗鲸', '静态'],
        'kind': 'static', 'author': '原作者未标注', 'source': '梗鲸',
        'sourceUrl': f'https://aigengtu.com/meme/{number}', 'originalUrl': url,
        'license': '站点说明：非营利粉丝向使用；版权归原作者',
        'licenseUrl': 'https://github.com/the-beating-light-of-the-nail/deepseek-chan-meme-pack#下载与使用微信--qq--dsh-meme',
        **save_image(url, f'gengjing-{number}{Path(url).suffix}'),
    }


def gif_item(card):
    link = card.select_one('.work-title')
    url = urllib.parse.urljoin(BASE, link['href'])
    page = BeautifulSoup(fetch(url), 'html.parser')
    data = next(json.loads(x.string) for x in page.select('script[type="application/ld+json"]')
                if json.loads(x.string).get('@type') == 'ImageObject')
    original = page.select_one('a[data-download-work]')['href']
    slug = card['data-slug']
    title = data['name']
    mood = next((m for m, words in [('干饭', '吃|舔|薯条'), ('委屈', '哭|哈气|懵|擂嘴'),
                ('贴贴', '蹭|扑|波波|双击|头追'), ('摸鱼', '旋转|摇尾巴')]
                if re.search(words, title)), '开心')
    preview_url = urllib.parse.urljoin(BASE, card.select_one('img')['src'])
    preview = save_image(preview_url, f'{slug}-preview.webp')['image']
    return {
        'id': f'bluefish-{slug}', 'title': title, 'alt': card.select_one('img')['alt'],
        'mood': mood, 'desc': '点开看看会动的小鱼，也可以保存原始 GIF。',
        'tags': [mood, '动图', 'GIF', '蓝色大肥鱼', *data.get('keywords', '').split(',')],
        'kind': 'gif', 'author': data.get('creditText', '原作者未标注'),
        'source': '蓝色大肥鱼开放档案', 'sourceUrl': url, 'originalUrl': original,
        'license': card.select_one('.art-license')['title'],
        'licenseUrl': data.get('license', BASE + '/about.html#license'),
        'preview': preview, 'previewUrl': preview_url,
        **save_image(original, f'{slug}.gif', animated=True),
    }


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(fetch('https://aigengtu.com/gallery-index.json'))
    entries = [entry for group in catalog['gallery'].values() for entry in group['images']]
    by_id = {Path(urllib.parse.urlparse(x['original']).path).stem: x for x in entries}
    by_id.setdefault('123', {'original': 'https://img.aigengtu.com/meme/123.webp', 'name': '我能去你家吃饭吗，就一碗'})
    # Interleave moods so the first screen is varied.
    selected = [(by_id[f'{ids[i]:03d}'], mood) for i in range(10) for mood, ids in SELECTION.items()]
    cards = []
    for url in [BASE + '/gifs.html', BASE + '/gifs/page/2.html']:
        cards.extend(BeautifulSoup(fetch(url), 'html.parser').select('article.work-card'))
    excluded = {'吊起来打', '中美AI大战', 'ZAKOZAKO', '薇欧鲸·深海回眸'}
    cards = [c for c in cards if c.select_one('.work-title').get_text(strip=True) not in excluded][:31]
    if len(cards) < 30:
        raise ValueError(f'Expected 30 GIF cards, found {len(cards)}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        stills = list(pool.map(static_item, selected))
        print('Downloaded and verified 50 still images', flush=True)
        gifs = []
        for card, future in zip(cards, [pool.submit(gif_item, c) for c in cards]):
            try:
                gifs.append(future.result())
            except ValueError as exc:
                print(f'Skipping non-animated file: {card["data-slug"]}: {exc}', flush=True)
        gifs = gifs[:30]
        if len(gifs) != 30:
            raise ValueError(f'Only {len(gifs)} verified animations')
    # Mix formats without changing stable IDs used by favorites.
    records = []
    for i, entry in enumerate(stills):
        records.append(entry)
        if i < len(gifs):
            records.append(gifs[i])
    if len({x['sha256'] for x in records}) != 80:
        raise ValueError('Duplicate image files in selection')
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    (SITE / 'gallery-data.js').write_text('// Imported 2026-11-08; provenance: assets/imported/sources.json\nconst importedStickers = ' + payload + ';\n', encoding='utf-8')
    (ASSETS / 'sources.json').write_text(payload + '\n', encoding='utf-8')
    print(f'Imported {len(records)} images; originals {sum(x["bytes"] for x in records)/1024/1024:.1f} MiB', flush=True)


if __name__ == '__main__':
    main()
