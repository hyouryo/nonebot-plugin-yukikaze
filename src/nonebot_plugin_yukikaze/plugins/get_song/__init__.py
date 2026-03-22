import json

import aiohttp
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageSegment as onebotv11MessageSegment

song = on_command("点歌")

search_url = "http://127.0.0.1:3000/search?keywords="
get_song_audio = "http://127.0.0.1:3000/song/url/v1?id="
get_song_url = "https://music.163.com/#/song?id="
get_song_audio2 = "&level=exhigh"
get_song_info = "http://127.0.0.1:3000/song/detail?ids="


@song.handle()
async def _(message: Message = CommandArg()):
    search_song_name = message.extract_plain_text()
    async with aiohttp.ClientSession() as session:
        get_search = search_url + search_song_name
        async with session.get(get_search) as response:
            # 搜索歌曲
            song_dict = json.loads(await response.text())
            song_id = song_dict["result"]["songs"][0]["id"]
        async with session.get(
            get_song_audio + str(song_id) + get_song_audio2
        ) as response:
            # 获取歌曲链接
            song_audio_dict = json.loads(await response.text())
            song_audio = song_audio_dict["data"][0]["url"]
            song_url = get_song_url + str(song_id)
        async with session.get(get_song_info + str(song_id)) as response:
            # 获取歌曲信息
            song_dict = json.loads(await response.text())
            song_name = song_dict["songs"][0]["name"]
            song_img = song_dict["songs"][0]["al"]["picUrl"]
            song_author = ""
            for i in song_dict["songs"][0]["ar"]:
                song_author += i["name"] + "/"
            song_author = song_author[:-1]
            # 发送歌曲
    sand_msg = onebotv11MessageSegment.music_custom(
        url=song_url,
        audio=song_audio,
        title=song_name,
        img_url=song_img,
        content=song_author,
    )
    await song.send(sand_msg)
