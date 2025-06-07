from nonebot import get_plugin_config,on_command, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, Bot, Event, MessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg,ArgPlainText
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher

from .config import Config
from .kardparse import codeCheck, codeAnalyze, countryList, deckList
from .draw import drawDeck
from .utils import get_file
from .database_processer import FuzzyQuery2c, RandomChoice, FetchData, UpdateData, QueryDataExist, WriteInData, FetchAllData, RemoveData
from .standardization import cardInfo, cropPic, getGuessImg, callInfo

from nonebot_plugin_waiter import waiter

import random
import traceback
import shortuuid

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import At, Target, UniMessage,CustomNode
from nonebot_plugin_alconna.uniseg import MsgTarget

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_kardsman",
    description="这是为卡牌游戏KARDS提供功能的插件",
    usage="",
    config=Config,
)

plugin_config = get_plugin_config(Config)
Kards_resource = plugin_config.Kards_resource

#--- 绘制卡组 ---
decks = on_command("绘制卡组")
@decks.handle()
async def _(msg: Message = CommandArg()):
    raw_args = msg.extract_plain_text().strip()
    if codeCheck(raw_args):
        deck = codeAnalyze(raw_args)
        deckL = deckList(codeAnalyze(raw_args))
        sorted_deck = sorted(deckL, key=lambda card_code: FetchData("Cards", "Cost", f'DeckCode="{card_code}"'))
        print(sorted_deck)
        if len(deckL)>39:
            await decks.finish("这个卡组码的卡片数量超过40了喔，检查一下吧！")
        else:
            try:
                await UniMessage.image(path=drawDeck(countryList(deck), sorted_deck)).send()
            except:           
                print(traceback.format_exc())
                await decks.finish("卡组码不对喔，检查一下吧！")
    else:
        await decks.finish("卡组码不对喔，检查一下吧！")

#--- 随机一卡 ---
draw = on_command("卡兹抽卡")
@draw.handle()
async def _():
    await UniMessage.image(path=random.choice(get_file(f"{Kards_resource}/cards/"))).send()

#--- 查询卡牌 ---
search = on_command("卡兹查卡")
@search.handle()
async def _(bot: Bot, msg: Message = CommandArg()):
    raw_args = msg.extract_plain_text().strip()
    if len(raw_args) > 0:
        msgall = []
        Cards = FuzzyQuery2c("Cards","CardName", "Effect", raw_args)
        cardI = cardInfo(Cards)
        if len(Cards) == 0:
            msgall.append(UniMessage.text("没有查找到相关卡牌"))
        elif len(Cards) > 10:
            msgall.append(UniMessage.text("查找到的项目较多，自动隐藏卡图"))
            for i in cardI:
                msgall.append(UniMessage.text(i[0]))
        else:
            for i in cardI:
                msgall.append(UniMessage.text(i[0]).image(path=f'{Kards_resource}/cards/{i[1]}.png'))
    else:
        await search.finish("没有输入卡名喔，再来一遍吧")
    await UniMessage.reference(*[
            CustomNode(uid=bot.self_id, name="kardsman", content=msg)
            for msg in msgall
        ]
    ).send()


#--- 猜卡部分 ---
guess = on_command("卡兹猜卡")
@guess.handle()
async def _():
    ask = RandomChoice("Cards")[0]
    print(ask)
    alias = ask[10].split("#")
    await UniMessage.text("你有45s的时间猜出这张卡，你可尝试5次\n").image(path=getGuessImg(cropPic(f'{Kards_resource}/cards/{ask[0]}.png'))).send() # type: ignore
    count = 5
    @waiter(waits=["message"], keep_session=True)
    async def check(event: Event):
        return event.get_plaintext()
    async for resp in check(timeout=45, retry=4, prompt=""):
        print(resp)
        if resp is None:
            await UniMessage.text(f'这张卡其实是：{ask[2]}!\n').image(path=f'{Kards_resource}/cards/{ask[0]}.png').send()
            break
        if resp in alias:
            await UniMessage.text(f'没错！这张卡就是：{resp}!\n').image(path=f'{Kards_resource}/cards/{ask[0]}.png').send()
            break
        if resp is not None:
            if  count == 5:
                await UniMessage.text(f'不是这张卡喔，偷偷告诉你，这张卡的国家是{ask[4]}').send()
                count -=1
            elif count == 4:
                await UniMessage.text(f'不是这张卡喔，偷偷告诉你，这张卡的类型是{ask[6]}').send()
                count -=1
            elif count == 3:
                await UniMessage.text(f'不是这张卡喔，偷偷告诉你，这张卡的稀有度是{ask[5]}').send()
                count -=1
            elif count == 2:
                await UniMessage.text(f'不是这张卡喔，偷偷告诉你，这张卡的费用是{ask[7]}\n这是最后一次机会了').send()
                count -=1
            else:
                await UniMessage.text(f'这张卡其实是：{ask[2]}!\n').image(path=f'{Kards_resource}/cards/{ask[0]}.png').send()
                count -=1
#未完成 发车部分
call = on_command("卡兹击剑")
@call.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, msg: Message = CommandArg()):
    if QueryDataExist("Call", "Caller", f'Caller="{event.user_id}"'):
        await UniMessage.text(f'你已经有一条击剑邀请了').send()
        await bot.finish()
    else:
        if msg.extract_plain_text():
            matcher.set_arg("Info", msg)

@call.got("Info", prompt="请输入击剑邀请信息")
async def _(bot:Bot, event: MessageEvent, target: MsgTarget, Info: str = ArgPlainText()):
    joinid=shortuuid.ShortUUID(alphabet="abcdefg").random(4)
    WriteInData("Call",'Caller,sendGroup,CallerName,Note,JoinID',f'{event.user_id},{target.id},"{event.sender.nickname}","{Info}","{joinid}"')
    broadCastList = FetchAllData("BroadCast", "*")
    for i in broadCastList:
        await bot.send_group_msg(group_id=i, message=callInfo(event.user_id, event.sender.nickname, Info, joinid))
    await UniMessage.text(f'击剑邀请已经广播').send()

joinbattle = on_command("加入击剑")
@joinbattle.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    if msg.extract_plain_text():
        matcher.set_arg("code", msg)

@joinbattle.got("code", prompt="请输入房间代码")
async def _(code: str = ArgPlainText()):
    if QueryDataExist("Call","JoinID",f'JoinID="{code}"'):
        info = FetchData("Call", "Caller, sendGroup", f'JoinID="{code}"')[0]
        print(info)
        await UniMessage([At("user", info[0]),"有人接受你的击剑邀请了！"]).send(target=Target(id=str(info[1])))
        await UniMessage.text(f'已经通知了房主').send()
        RemoveData("Call", f'JoinID="{code}"')
        
fetchbattle = on_command("还有谁要击剑")
@fetchbattle.handle()
async def _(bot: Bot):
    alldata = FetchAllData("Call", 'Caller,CallerName,Note,JoinID')
    msgall = []
    if len(alldata) == 0:
        msgall.append(UniMessage.text("现在还没有人想要击剑"))
        await UniMessage.reference(*[
            CustomNode(uid=bot.self_id, name="Amadeus", content=msg)
            for msg in msgall
        ]
        ).send()
    else:
        for i in alldata:
            msgall.append(UniMessage.text(callInfo(i[0],i[1],i[2],i[3])))
        await UniMessage.reference(*[
            CustomNode(uid=bot.self_id, name="Amadeus", content=msg)
            for msg in msgall
        ]
        ).send()

openBroadcast = on_command("开启击剑广播", permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER)
@openBroadcast.handle()
async def _(bot: Bot, event: MessageEvent, target: MsgTarget,):
    if QueryDataExist("BroadCast","GruopID",f"GruopID={target.id}"):
        await UniMessage.text(f'这个群已经开启过了击剑广播').send()
    else:
        WriteInData("BroadCast", 'GruopID', f'{target.id}')
        await UniMessage.text(f'这个群开启了击剑广播').send()

closeBroadcast = on_command("关闭击剑广播", permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER)
@closeBroadcast.handle()
async def _(bot: Bot, event: MessageEvent, target: MsgTarget,):
    if QueryDataExist("BroadCast","GruopID",f"GruopID={target.id}"):
        RemoveData("BroadCast", f"GruopID={target.id}")
        await UniMessage.text(f'这个群关闭了了击剑广播').send()
    else:
        await UniMessage.text(f'这个群已经关闭过了击剑广播').send()

removebattle = on_command("停止击剑")
@removebattle.handle()
async def _(bot: Bot, event: MessageEvent):
    if QueryDataExist("Call", "Caller", f'Caller="{event.user_id}"'):
        RemoveData("Call", f"Caller={event.user_id}")
        await UniMessage.text(f'已经移除了你的击剑邀请').send()
    else:
        await UniMessage.text(f'你还没有发出的击剑邀请').send()
#添加别名
addalias = on_command("添加别名", permission=SUPERUSER)
@addalias.handle()
async def _(msg: Message = CommandArg()):
    raw_args = msg.extract_plain_text().strip()
    args = raw_args.split("/")
    oldInfo = FetchData("Cards", "Alias", f'CardName="{args[0]}"')[0][0]
    UpdateData("Cards", "Alias", f'"{oldInfo}#{args[1]}"', f'CardName="{args[0]}"')
    newInfo = FetchData("Cards", "Alias", f'CardName="{args[0]}"')[0][0]
    await UniMessage.text(f'完成！现在卡牌{args[0]}的别名列表如下：\n{newInfo}').send()