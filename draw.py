#--本模块负责绘制卡组图片--
from PIL import Image, ImageDraw ,ImageFont
from nonebot import get_plugin_config
from .config import Config
from .utils import country, get_file
from .database_processer import FetchData
from pathlib import Path
import random

picSize = [250,351]
startPixel = [102,339]

plugin_config: Config = get_plugin_config(Config)
Kards_resource = plugin_config.Kards_resource

#这里传入的deck应当是一整个列表，重复的卡重复加入列表
#形如["aa","aa","bb","cc"]
def drawDeck(countries,deck):
    #卡组绘制逻辑
    cardPosNow = [0,0]
    bg = Image.open(f'{Kards_resource}/bg.png')
    for i in deck:
        cardCode = FetchData("Cards","PicID",f'DeckCode="{i}"')[0][0]
        card = Image.open(f'{Kards_resource}/cards/{cardCode}.png')
        bg.paste(card.resize(picSize), (startPixel[0]+(cardPosNow[0]*250),startPixel[1]+(cardPosNow[1]*351)))
        if cardPosNow[0] < 9:
            cardPosNow[0] += 1
        else:
            cardPosNow[1] += 1
            cardPosNow[0] = 0
    #文字绘制逻辑
    ttf_path = f'{Kards_resource}/fonts/dengxiancu.ttf'
    ttfc = ImageFont.truetype(ttf_path, 100)
    ttfn = ImageFont.truetype(ttf_path, 200)
    img_draw = ImageDraw.Draw(bg)
    img_draw.text((1883, 88), country[countries[0]], font=ttfc, fill=(255,255,255))
    img_draw.text((1883, 191), country[countries[1]], font=ttfc, fill=(255,255,255))
    img_draw.text((2180, 22), f'{len(deck)+1}', font=ttfn, fill=(255,255,255))
    #填个表情包  这个部分是史山  需要重构
    memeList = get_file(f"{Kards_resource}/memes")
    while cardPosNow[0] < 9 or cardPosNow[1] < 3 :
        meme = Image.open(random.choice(memeList))
        meme.thumbnail((250,351))
        bg.paste(meme, (startPixel[0]+(cardPosNow[0]*250),startPixel[1]+(cardPosNow[1]*351)))
        if cardPosNow[0] < 9:
            cardPosNow[0] += 1
        else:
            cardPosNow[1] += 1
            cardPosNow[0] = 0
    meme = Image.open(random.choice(memeList))
    meme.thumbnail((250,351))
    bg.paste(meme, (2352,1392))
    #保存图片
    outDir =  Path(f'{Kards_resource}/output') 
    if not outDir.exists():
        outDir.mkdir(exist_ok=True, parents=True)
    outPath = f'{Kards_resource}/output/output.png'
    bg.save(outPath)
    return outPath