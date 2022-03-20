import os
import re
import aiohttp
import asyncio
import pathlib
import argparse
from tqdm import tqdm

location = "./_stickers"


def extract_pack_id(input_string):
    url_pattern = r"https:\/\/store.line.me\/stickershop\/product\/(\d+)"
    if input_string.isdigit():
        return int(input_string)
    match = re.search(url_pattern, input_string)
    if match:
        return int(match.group(1))
    raise ValueError(
        "Invalid ID or URL. Please provide a valid sticker pack ID or URL."
    )


async def fetch_metadata(session, url):
    async with session.get(url) as response:
        return await response.text()


async def download_sticker(session, url, file_name):
    async with session.get(url) as response:
        content = await response.read()
        with open(file_name, "wb") as f:
            f.write(content)


async def main(pack_input):
    pack_id = extract_pack_id(pack_input)

    metadata_url = f"https://stickershop.line-scdn.net/products/0/0/1/{pack_id}/android/productInfo.meta"

    async with aiohttp.ClientSession() as session:
        metadata = await fetch_metadata(session, metadata_url)

    re_title_pattern = r'(?<=title\"\:\{\"en\"\:\")(.*?)(?=")'
    en_title_re = re.search(re_title_pattern, metadata)
    en_title = en_title_re.group() if en_title_re else "Unknown"
    en_title = bytes(en_title.replace("\\\\", "\\"), "utf-8").decode("unicode_escape")

    re_id_pattern = r"(?<=\"id\"\:)(.*?)(?=\,)"
    start_id_str = re.search(re_id_pattern, metadata)
    end_id_str = re.findall(re_id_pattern, metadata)[-1]
    start_id = int(start_id_str.group()) if start_id_str else 0
    end_id = int(end_id_str) + 1

    pack_folder = os.path.join(location, en_title)
    pathlib.Path(pack_folder).mkdir(parents=True, exist_ok=True)
    os.chdir(pack_folder)

    amount = end_id - start_id
    print(f'Start downloading {amount} sticker(s) of "{en_title}" pack:\n')

    pbar = tqdm(
        total=amount,
        desc="Downloading",
        bar_format="{desc}: |{bar}| {n_fmt}/{total_fmt}",
    )

    async with aiohttp.ClientSession() as session:
        tasks = []
        for current_id in range(start_id, end_id):
            file_name = f"{current_id}.png"
            sticker_url = f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{current_id}/ios/sticker@2x.png"
            tasks.append(download_sticker(session, sticker_url, file_name))
            pbar.update(1)
        await asyncio.gather(*tasks)

    pbar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download LINE sticker pack.")
    parser.add_argument("pack_input", type=str, help="Sticker pack ID or URL.")
    args = parser.parse_args()

    asyncio.run(main(args.pack_input))
