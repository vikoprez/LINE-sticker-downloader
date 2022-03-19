import os
import io
import re
import mmap
import urllib.request as urlrq
import pathlib
from tqdm import tqdm

location = './_stickers'

# type sticker pack's id
pack_id = int(input("Type sticker pack's ID: "))

# download productInfo.meta file and open as string to take values needed
urlrq.urlretrieve(f'https://stickershop.line-scdn.net/products/0/0/1/{pack_id}/android/productInfo.meta', 'metadata')
with io.open('./metadata', mode='r', encoding='utf-8') as f:
	metadata = str(mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ).read())

# take sticker pack's name
re_title_pattern = r'(?<=title\"\:\{\"en\"\:\")(.*?)(?=")'
en_title_re = re.search(re_title_pattern, metadata)
if en_title_re:
	en_title_un = en_title_re.group()
en_title = bytes(en_title_un.replace('\\\\', '\\'), 'utf-8').decode('unicode_escape') # the title is not encoded in some cases, for example with pack 3951669 it is fucking returned unicode backslash code of &

# take id
re_id_pattern = r'(?<=\"id\"\:)(.*?)(?=\,)'
start_id_str = re.search(re_id_pattern, metadata)
end_id_str = re.findall(re_id_pattern, metadata)[-1]
if start_id_str:
	start_id = int(start_id_str.group())
if end_id_str:
	end_id = int(end_id_str) + 1

# make folder with sticker pack's title and enter
pack_folder = location + f'/{en_title}'
pathlib.Path(pack_folder).mkdir(parents=True, exist_ok=True)
os.chdir(pack_folder)

# download
amount = end_id - start_id # they're 40 stickers in mostly every pack but u sure want to have a correct number for the worst case
count = 1
print(f'Start downloading {amount} sticker(s) of "{en_title}" pack:\n')

# progress bar
pbar = tqdm(range(amount), desc='Downloading', bar_format='{desc}: |{bar}| {n_fmt}/{total_fmt}')

for current_id in range(start_id, end_id):
	file_name = '{}.png'.format(current_id)
	urlrq.urlretrieve(f'https://stickershop.line-scdn.net/stickershop/v1/sticker/{current_id}/ios/sticker@2x.png', file_name)
	# time.sleep(0.1) # time is valuable so alap
	pbar.update(1)
	# print('Downloaded {} of {} stickers\r'.format(count, amount))
	# count += 1
	# use these in case you don't want tqdm
pbar.close()

# delete metadata file, only leave stickers left
os.remove('../../metadata')

# exit ofc but immediately so no need below
# input('\nDone! Press Enter to exit...')
