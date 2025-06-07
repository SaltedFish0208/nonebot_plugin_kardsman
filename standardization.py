#本模块负责标准化返回的数据
import math
import random
from typing import Optional
from PIL import Image
from nonebot import get_plugin_config
from .char import charPic
from .config import Config
from pathlib import Path

plugin_config: Config = get_plugin_config(Config)
Kards_resource = plugin_config.Kards_resource

def cardInfo(data):
    msg = []
    for i in data:
        CInfo = [f'🔥卡名：{i[2]}\n✨效果：{i[3]}\n🌍国家：{i[4]}\n🌟稀有度：{i[5]}\n🎴卡片类型：{i[6]}\n⚡️部署消耗：{i[7]}\n⚡️行动消耗：{i[8]}\n📦卡包：{i[9]}',f'{i[0]}']
        msg.append(CInfo)
    return msg

def getRandom(num: int) -> int:
    return random.randint(1, num) % num


def getGuessImg(image: Image, restrict=3) -> Image:
    height, weight = image.size
    re_num = getRandom(restrict)
    # 模糊处理
    if re_num == 1:
        image.thumbnail((height / 7 , weight / 7), Image.LANCZOS)
        height, weight = image.size
        image = image.resize((height * 7, weight * 7))
    # 切割处理
    elif re_num == 2:
        sqrt = math.sqrt(6)
        beSqrt = 6 / sqrt
        cut = (sqrt, beSqrt) if getRandom(2) == 1 else (beSqrt, sqrt)
        cutHeight, cutWeight = int(image.size[0] / cut[0]), int(image.size[1] / cut[1])
        cutX, cutY = random.randint(cutHeight, height - cutHeight), random.randint(cutWeight, weight - cutWeight)
        image = image.crop((cutX, cutY, cutX + cutHeight, cutY + cutWeight))
    # 字符画
    else:
        image = charPic(image)
    outDir =  Path(f'{Kards_resource}/output') 
    if not outDir.exists():
        outDir.mkdir(exist_ok=True, parents=True)
    outPath = f'{Kards_resource}/output/output2.png'
    image.save(outPath)
    return outPath

def cropPic(picPath: str):
    pic = Image.open(picPath)
    croppic = pic.crop((12, 100, 487, 450))
    return croppic

def callInfo(caller:int, callername:Optional[str], info:str, joinID:str):
    CInfo = f'[邀请击剑人]{callername}({caller})\n[邀请信息]{info}\n输入 "加入击剑 {joinID}" 来加入对局'
    return CInfo