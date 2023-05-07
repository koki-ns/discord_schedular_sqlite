import discord
from discord.ext import tasks
import re
import datetime
import logging
import json

from calendarDB import calendarDB

token_file = "discord_token.json"

with open(token_file) as f:
    d = json.load(f)
TOKEN = d["token"]
CHANNEL_ID = None

fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename='discord.log', level=logging.DEBUG, format=fmt)
#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

db = calendarDB("calendar")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    morning_call.start()
    channels = client.get_all_channels()
    channel = next(channels).channels[0]
    await channel.send("botが起動しました。/setchannelコマンドでモーニングコールの投稿先設定を行ってください。")
    print(f'We have logged in as {client.user}')
    
@tree.command(
    name="setchannel",
    description="モーニングコールの投稿先を変更します"
)
@discord.app_commands.guild_only()
async def setchannel(interaction:discord.Interaction):
    global CHANNEL_ID
    CHANNEL_ID = interaction.channel_id
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("朝の通知の送信先をこのチャンネルに変更しました。")
    

@tree.command(
    name="hello",
    description="Send Hello world."
    )
async def hello(ctx):
    await ctx.send('Hello!')
    
@tree.command(
    name="addcalendar",
    description="カレンダーに予定を追加"
    )
@discord.app_commands.guild_only()
async def addcalendar(interaction:discord.Interaction, day:str, summary: str, year: str=None, time_start: str=None, time_end: str=None):
    try:
        summaries = summary.split(" ")

        #構文が正しいか解析する処理
        if re.fullmatch(r"([1-9]|0[1-9]|1[0-2])/([1-9]|[0-2][0-9]|3[0-1])", day) is None:
            await interaction.response.send_message("エラー：日付が不正です")
            return
        
        if year is not None and re.fullmatch(r"20[0-9][0-9]", year) is None:
            await interaction.response.send_message("エラー：西暦が不正です")
        
        #時刻のバリデーション
        if time_start is None or time_end is None:
            time_start = None
            time_end = None
        elif ((re.fullmatch(r"([1-9]|0[1-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9])", time_start) is None or re.fullmatch(r"([1-9]|0[1-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9])", time_end)) is None) and time_start is  not None:
            await interaction.response.send_message("エラー：時刻が不正です")
            return
        
        #dateとsummaryの構築
        if year is None:
            year = str(datetime.date.today().year)
            
        month_and_day = day.split("/")
        date_start = year + "-" + month_and_day[0] + "-" + month_and_day[1]
        target_datetime = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        
        result = datetime.datetime.strftime(target_datetime, '%Y/%m/%d') + " 予定追加：\n"
        result_log = datetime.datetime.strftime(target_datetime, '%Y/%m/%d') + "に予定を追加："
        
        for sum in summaries:
            result = result + "・" + sum + "\n"
            result_log = result_log + " " + sum
            
        db.insert_event(target_datetime, summaries)
        
        """
        for sum in summaries:
            ec.insert_event(date_start, date_end, sum)
            #await ctx.send("start:{0}, end:{1}, summary:{2}".format(date_start, date_end, summary))
            result = result + "・" + sum + "\n"
            result_log = result_log + " " + sum
        """
        
        await interaction.response.send_message(result)
        logging.info(result_log)
        
        
    except:
        await interaction.response.send_message("何かしらのエラーが発生しました")
    #インデックスエラー、構文エラー
    #await ctx.send(arguments)
    
async def fetch_event(date: datetime.datetime):
    text = datetime.datetime.strftime(date, "%Y/%m/%d") + "の予定:" + "\n"
    event_list = db.get_posts(date)
    
    if event_list:
        for event in event_list:
            if event[3] == 0:
                # statusが1(完了)ならチェックマークを表示したい 0は未完了
                top = "・"
            else:
                top = "\N{White Heavy Check Mark}"
            text = text + top + event[2] + "*（id:" + str(event[0]) + "）*"+ "\n"
    else:
        text = text + "登録された予定はありません"
    
    return text

@tree.command(
    name="show_events",
    description="指定された日の予定を表示します。指定がなければ今日の予定を表示します。"
)
@discord.app_commands.guild_only()
async def show_events(interaction: discord.Interaction, day: str=None, year: str=None):
    if day == None:
        #引数がなければ今日の予定を表示
        target_datetime = datetime.datetime.today()
    elif re.fullmatch(r"([1-9]|0[1-9]|1[0-2])/([1-9]|[0-2][0-9]|3[0-1])", day) is None:
        await interaction.response.send_message("日付の入力が不正です")
        return
    else:
        #dateとsummaryの構築
        if year is None:
            year = str(datetime.date.today().year)
            
        month_and_day = day.split("/")
        date_start = year + "-" + month_and_day[0] + "-" + month_and_day[1]
        target_datetime = datetime.datetime.strptime(date_start, '%Y-%m-%d')
    text = await fetch_event(target_datetime)
    await interaction.response.send_message(text)
    logging.info("today_events is called")
    
@tree.command(
    name="set_status",
    description="指定したidのイベントのステータスを変更します。0:未完了 1:完了"
)
@discord.app_commands.guild_only()
async def set_status(interaction: discord.Interaction, id: int, status: int):
    if status != 0 and status != 1:
        await interaction.response.send_message("ステータスは0か1で指定してください")
        return
    if db.set_status(id, status) == 0:
        await interaction.response.send_message("ステータスが更新されました")
    else:
        await interaction.response.send_message("ステータスの更新中にエラーが発生しました")
    
@tasks.loop(seconds=60)
async def morning_call():
    global CHANNEL_ID
    # 現在の時刻
    if CHANNEL_ID == None:
        
        return
    else:
        now = datetime.datetime.now()
        if now.hour == 7 and now.minute == 0:
            channel = client.get_channel(CHANNEL_ID)
            text = "おはようございます。\n本日の予定を通知します。\n"
            text = text + await fetch_event(now)
            await channel.send(text) 
            logging.info("morning call")
            
        elif now.hour == 21 and now.minute == 0:
            channel = client.get_channel(CHANNEL_ID)
            text = "21時になりました。\n明日の予定を通知します。\n"
            tomorrow = now + datetime.timedelta(days=1)
            text = text + await fetch_event(tomorrow)
            await channel.send(text) 
            logging.info("night call")


client.run(TOKEN)