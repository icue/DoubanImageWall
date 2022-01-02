import argparse
import os
import random
import re
import requests
import time
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, UnidentifiedImageError


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--id', type=str, required=True, help='User id, or a link containing it')
parser.add_argument('-o', '--offset', type=int, default=13,
                    help='In the first 4 rows, a larger image will occur once every {offset} cells.'
                    'The following rows repeat this pattern. Set to 0 to disable larger images.')
parser.add_argument('-c', '--col', type=int, default=5, help='Number of columns in the matrix')
parser.add_argument('-r', '--row', type=int, default=8, help='Number of rows in the matrix')
parser.add_argument('-w', '--width', type=int, default=540, help='Width of one cell. A value less than 600 is recommended.')
parser.add_argument('-ht', '--height', type=int, default=750, help='Height of one cell. A value less than 800 is recommended. Will be the same as cell width in music mode.')
parser.add_argument('-rd', '--random', type=bool, default=False, help='Whether to shuffle the images')
parser.add_argument('-rt', '--rating', type=int, default=0, help='Rating filter. Only integers between 1 (one star) and 5 (five stars) are meaningful')
parser.add_argument('-s', '--sort-by-time', type=bool, default=False,
                    help='Whether to sort chronologically (neareast first). Default is False, as default sort order is by rating.')
parser.add_argument('-m', '--mode', type=str, default='movie', choices=['movie', 'music'], help='"movie" or "music". In "music" mode, cell height will be the same as cell width.')
parser.add_argument('-t', '--threshold', type=int, default=300,
                    help='Number of cached images to pertain. Once the number goes beyond this threshold, '
                    'unused cache gets removed. Set to 0 to immediately remove unused cache after a run.')
parser.add_argument('-l', '--limit', type=int, default=200,
                    help='Limit of number of items to process. Default is 200. Raise this when COL x ROW > 200.')
parser.add_argument('--max-width', type=int, default=4000, help='Maximum width of the output in pixel number.')
parser.add_argument('--max-height', type=int, default=8000, help='Maximum height of the output in pixel number.')
args = parser.parse_args()
_MUSIC_MODE = args.mode == 'music'
_COLUMN_NUM = args.col
_ROW_NUM = args.row
_OFFSET = args.offset
_CELL_WIDTH = args.width
_CELL_HEIGHT = args.width if _MUSIC_MODE else args.height
_WIDTH = _CELL_WIDTH * _COLUMN_NUM
_HEIGHT = _CELL_HEIGHT * _ROW_NUM
_CACHE = 'cache/'
_OUTPUT = 'output/'

larger_image_index = []
if _OFFSET:
    for x in range(0, _COLUMN_NUM * 3, _OFFSET):
        for y in range(x, _COLUMN_NUM * _ROW_NUM, _COLUMN_NUM * 4):
            if y % _COLUMN_NUM >= _COLUMN_NUM - 1:
                print('Invalid offset. Try decrease or increase by 1.')
                exit()
            larger_image_index.append(y)
skip_image_index = [x for i in larger_image_index for x in (i + 1, i + _COLUMN_NUM, i + _COLUMN_NUM + 1) if x < _COLUMN_NUM * _ROW_NUM]
if any(x in larger_image_index for x in skip_image_index):
    print('Invalid offset. Try decrease or increase by 1.')
    exit()

if args.id.isnumeric() or 'douban.com' not in args.id:
    id = args.id
else:
    match = re.match('.*people/(.*)/.*', args.id)
    if not match:
        print('invalid id')
        exit()
    id = match[1]
start = range(0, args.limit, 15)
urls = (f'https://{args.mode}.douban.com/people/{id}/collect?'
        f'start={x}&sort={"time" if args.sort_by_time else "rating"}'
        f'&rating={"all" if args.rating<1 or args.rating>5 else args.rating}'
        f'&filter=all&mode=grid&tags_sort=count'
        for x in start)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.113 Safari/537.36'}

img_urls = []
enough_met = False
for url in urls:
    response = requests.get(url, headers=headers).text
    soup = BeautifulSoup(response, features='html.parser')
    items = soup.find_all('a', {'class': 'nbg'})
    if not items:
        break
    for a in items:
        img_urls.append(a.find('img', recursive=False)['src'])
        if len(img_urls) >= _COLUMN_NUM * _ROW_NUM - len(skip_image_index):
            enough_met = True
            break
    if enough_met:
        break
    time.sleep(5)
print(f'A total of {len(img_urls)} images to process.')
if args.random:
    random.shuffle(img_urls)

os.makedirs(_CACHE, exist_ok=True)
cache_imgs = {_CACHE + f: False for f in os.listdir(_CACHE) if os.path.isfile(_CACHE + f) and (f.lower().endswith('.jpg') or f.lower().endswith('.webp'))}

result = Image.new('RGB', (_WIDTH, _HEIGHT))
count = 0
img_iter = iter(img_urls)
for j in range(0, _HEIGHT, _CELL_HEIGHT):
    for i in range(0, _WIDTH, _CELL_WIDTH):
        if count in skip_image_index:
            count += 1
            continue
        try:
            image_url = next(img_iter)
        except StopIteration:
            break

        size = (_CELL_WIDTH, _CELL_HEIGHT)
        need_large = count in larger_image_index
        if need_large:
            size = (_CELL_WIDTH * 2, _CELL_HEIGHT * 2)
            if _MUSIC_MODE:
                image_url = image_url.replace('subject/s', 'subject/l')
            else:
                image_url = image_url.replace('s_ratio_poster', 'l_ratio_poster')
        elif _MUSIC_MODE:
            image_url = image_url.replace('subject/s', 'subject/m')
        else:
            image_url = image_url.replace('s_ratio_poster', 'm_ratio_poster')
        count += 1

        cache_img_name = _CACHE + image_url[image_url.rfind('/') + 1:]
        need_retrieve = True
        if cache_img_name in cache_imgs:
            need_retrieve = False
            print(f'Found cache for {image_url}: {cache_img_name}')
            cache_imgs[cache_img_name] = True
            img = Image.open(cache_img_name)
            if need_large and img.width < 600:
                print('...but size is smaller than needed. Will retrieve and overwrite.')
                need_retrieve = True
        if need_retrieve:
            print('Retrieving ' + image_url)
            response = requests.get(image_url, stream=True, headers=headers)
            try:
                img = Image.open(BytesIO(response.content))
            except:
                print('Failed to process. Trying again with webp...')
                time.sleep(3)
                image_url = image_url.replace('.jpg', '.webp')
                response = requests.get(image_url, stream=True, headers=headers)
                try:
                    img = Image.open(BytesIO(response.content))
                except:
                    print('Still failing! Trying again with larger image size...')
                    time.sleep(3)
                    if _MUSIC_MODE:
                        image_url = image_url.replace('subject/l', 'subject/b').replace('subject/m', 'subject/l')
                    else:
                        image_url = image_url.replace('l_ratio_poster', 'b_ratio_poster').replace('m_ratio_poster', 'l_ratio_poster')
                    response = requests.get(image_url, stream=True, headers=headers)
                    try:
                        img = Image.open(BytesIO(response.content))
                    except:
                        print('Still failing! Giving up.')
                        continue
            img.save(cache_img_name, optimize=True)
            time.sleep(3)

        result.paste(img.resize(size, Image.LANCZOS), (i, j))

result.thumbnail((args.max_width, args.max_height), Image.LANCZOS)
os.makedirs(_OUTPUT, exist_ok=True)
result.save(f'{_OUTPUT}/{id}_{args.mode}.jpg', optimize=True, quaility=80)

if len(cache_imgs) > args.threshold:
    for cached_img, used in cache_imgs.items():
        if not used:
            print(f'Removing unused cache {cached_img}...')
            os.remove(cached_img)
