# bot.py
import os
import discord
from dotenv import load_dotenv
import openai

import sys
import traceback
import numpy as np
import googletrans as ggt
import random
import re
import MBTI_prediction
from discord.ext import commands
import asyncio

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

# 創建空的權限物件
permissions = discord.Permissions()
# 使用權限整數值更新權限物件
permissions.update(int='permissions_int')

# Set up the OpenAI API client
openai.api_key = OPENAI_KEY

intents = discord.Intents.all()
#client = discord.Client(command_prefix='!', intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

bot_temperature = 0.5

characters = [ "酸民" , "正義人士" , "警察" , "囚犯" , "學生" , "導演" , "乞丐" , "歌手" , "愛國人士" , "外星人" , "和尚" ] 

sentiments = [ "喜悅" , "憤怒" , "悲傷" , "恐懼" , "厭惡" , "驚奇" , "羨慕" , "羞怯" ]

response_record = {}

member_stats = {}

bot_mbti_TF = {}

count_msg_bot = 0

global guild,channel,members

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  game = discord.Game('測試用機器人，輸入"$指令"查看功能')
  #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
  await bot.change_presence(status=discord.Status.idle, activity=game)
  
  guild = bot.guilds[0]  # 取得第一個伺服器的資訊

@bot.command()
async def MBTI_test(ctx):
    print("建立一個投票\n")
    question_JP = [
        ["你出國旅遊之前，通常會?"],
        ["當你某日想去某個地方，你會?"],
        ["你會比較喜歡?"],
        ["你對事物的規畫更注重?"],
        ["按日程表辦事對你而言是"],
        ["對於制定周末計劃，你認為?"],
        ["日常工作你更有可能?"],
        ["當有一項特殊工作時，你會?"],
        ["你覺得自己是一個偏好"],
        ["對於自己的一天你會怎麼過"],
        ["通常你面對一個急迫的大專案，你會"],
        ["你覺得計畫是"]
    ]
    option_JP = [
        ["列好每個行程，按計畫進行", "走到哪玩到哪，看心情決定"],
        ["計劃好將做的事情以及何時做","什麼都不事先想就去做" ],
        ["事先安排好約會，聚會","只要時機恰當就無拘無束地做任何事"],
        ["計畫性","即時性"],
        ["正合你意", "束縛了你"],
        ["有必要","沒必要"],
        ["先安排好工作並盡可能提早完成","在時間緊迫的狀況下分秒必爭的完成"],
        ["在開始前精心組織策劃","在工作進行中找出必要環節"],
        ["組織性的人","自發性的人"],
        ["按照既定的日程","看心情而定"],
        ["先規劃好要做的是併排好先後順序","把握時間，直接開始"],
        ["正確的","參考用"]
    ]

    question_SN = [
        ["當你學習新的事物時，你傾向?"],
        ["如果你是一位老師，你會想教?"],
        ["你通常和怎樣的人相處得更好?"],
        ["你願意自己被認為是一個"],
        ["你更喜歡怎樣的人?"],
        ["你更願意把怎樣的人當作朋友"],
        ["當你為了消遣而閱讀時"],
        ["做很多人都會做的事情時，你喜歡?"],
        ["對於事情遇到瓶頸時，你偏好"]

    ]
    option_SN = [
        ["天馬行空，喜歡開放性思考", "依照經驗，透過分析得到方向"],
        ["涉及事實的課程", "涉及理論的課程"],
        ["現實的人","想像力豐富的人"],
        ["善於實作的人","善於創意的人"],
        ["務實且有豐富常識的人","頭腦靈活的人"],
        ["腳踏實地","有新觀點"],
        ["善於接受作者所表達的意思","以奇特新穎的角度進行剖析"],
        ["按慣例做","按自己獨創的方式做 "],
        ["先以當前最可行替代方案來進行","不計代價，從錯誤中分析並挑戰未知的問題"]
    ]

    question_EI = [
        ["你在哪個情況比較能夠開心?"],
        ["你通常是一位"],
        ["當你和一群人在一起時，你會"],
        ["在大群體中，更多時候你是?"],
        ["你覺得通常別人要花費"],
        ["出門逛街時你喜歡?"],
        ["你更善於?"],
        ["對於新認識的人，你會?"],
        ["你認為大多數的人對你的評價是"],
        ["如果被很多人圍著，你會感到?"],
        ["在聚會中，你通常會覺得"],
        ["你覺得別人要了解你是很?"],
        ["在聚會中你通常?"]
    ]
    option_EI = [
        ["出門，和朋友或家人相聚", "獨處，一個人追劇打電動"],
        ["一個善於交際的人", "安靜緘默的人"],
        ["參加大家的談話","只同你熟知的人單獨談話 "],
        ["介紹他人", "由別人來介紹你 "],
        ["一小段時間來瞭解你","很久來瞭解你"],
        ["約人一起逛","自己逛"],
        ["只要願意就能跟任何人談天說地","只在特定場合或人士的情況下談天說地"],
        ["馬上跟對方分享你的興趣","待更熟悉彼此之後才會去聊"],
        ["非常坦率","不太會脫口而出自己的事"],
        ["更有精神","心神不寧"],
        ["很享受","很壓抑"],
        ["簡單","困難"],
        ["自己聊得多","聽別人得多"]
    ]

    question_FT = [
        ["當你在與人溝通時，你會優先?"],
        ["你往往會是一個?"],
        ["你覺得被稱為怎樣的人你比較開心?"],
        ["你更傾向於"],
        ["做決定時，你會優先考慮?"],
        ["你會願意在一個怎麼樣的上司底下工作?"],
        ["你認為怎樣的人較會受人讚賞?"]
    ]
    option_FT = [
        ["以對方感受為重，和諧相處", "先確認是否合乎邏輯或公平性"],
        ["情感駕馭理智", "理智駕馭情感 "],
        ["感性的人","理性的人"],
        ["憑感覺做事","以邏輯思考來行事"],
        ["別人的感受和觀點","依照事實來衡量"],
        ["脾氣好，但前後不一","很嚴厲，但有條理"],
        ["有同情心","有競爭力"]
    ]

    poll_messages = []  # 儲存每個問題的投票訊息
    poll_results = {}  # 儲存每個問題的投票結果

    total_question_num = 4

    selec_indices_EI = random.sample(range(len(question_EI)), int(total_question_num/4))
    selected_question_EI = [question_EI[index] for index in selec_indices_EI]
    selected_option_EI = [option_EI[index] for index in selec_indices_EI]
    EI_counts = 0
    
    selec_indices_SN = random.sample(range(len(question_SN)), int(total_question_num/4))
    selected_question_SN = [question_SN[index] for index in selec_indices_SN]
    selected_option_SN = [option_SN[index] for index in selec_indices_SN]
    SN_counts = 0
    
    selec_indices_FT = random.sample(range(len(question_FT)), int(total_question_num/4))
    selected_question_FT = [question_FT[index] for index in selec_indices_FT]
    selected_option_FT = [option_FT[index] for index in selec_indices_FT]
    FT_counts = 0

    selec_indices_JP = random.sample(range(len(question_JP)), int(total_question_num/4))
    selected_question_JP = [question_JP[index] for index in selec_indices_JP]
    selected_option_JP = [option_JP[index] for index in selec_indices_JP]
    JP_counts = 0

    questions = []
    option_1 = []
    option_2 = []
    for i in range(total_question_num):
        if i%4 == 0:
            questions.append(selected_question_EI[EI_counts])
            option_1.append(selected_option_EI[EI_counts][0])
            option_2.append(selected_option_EI[EI_counts][1])
            EI_counts += 1
        elif i%4 == 1:
            questions.append(selected_question_SN[SN_counts])
            option_1.append(selected_option_SN[SN_counts][0])
            option_2.append(selected_option_SN[SN_counts][1])
            SN_counts += 1
        elif i%4 == 2:
            questions.append(selected_question_FT[FT_counts])
            option_1.append(selected_option_FT[FT_counts][0])
            option_2.append(selected_option_FT[FT_counts][1])
            FT_counts += 1
        elif i%4 == 3:
            questions.append(selected_question_JP[JP_counts])
            option_1.append(selected_option_JP[JP_counts][0])
            option_2.append(selected_option_JP[JP_counts][1])
            JP_counts += 1
        
        poll_message = f"{questions[i]}\n"
        poll_message += "1. :one: {}\n".format(option_1[i])
        poll_message += "2. :two: {}\n".format(option_2[i])

        poll_embed = discord.Embed(description=poll_message, color=discord.Color.blue())
        poll_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        poll = await ctx.send(embed=poll_embed)

        await poll.add_reaction("1️⃣")  # :one: 的 Unicode 符號
        await poll.add_reaction("2️⃣")  # :two: 的 Unicode 符號

        poll_messages.append(poll)  # 儲存投票訊息
        poll_results[poll.id] = {"option_1": 0, "option_2": 0}  # 初始化投票結果

    # 等待投票結束
    while True:
        await asyncio.sleep(10)  # 每隔 60 秒檢查一次投票狀態
        
        finished = True  # 假設所有問題的投票都已結束
        for poll in poll_messages:
            message = await ctx.fetch_message(poll.id)
            for reaction in message.reactions:
                if reaction.emoji == "1️⃣":
                    poll_results[poll.id]["option_1"] = reaction.count - 1  # 減去機器人自身的反應
                elif reaction.emoji == "2️⃣":
                    poll_results[poll.id]["option_2"] = reaction.count - 1  # 減去機器人自身的反應
            if poll_results[poll.id]["option_1"] == 0 and poll_results[poll.id]["option_2"] == 0:
                print("Not yet.")
                finished = False  # 如果有任何一個問題的投票還沒結束，則將 finished 設為 False
                break
        if finished:
            break

    # 處理投票結果
    EI_type=0
    SN_type=0
    TF_type=0
    JP_type=0
    
    print("投票結果：")
    for i, poll in enumerate(poll_messages):
        than_size = True
        question = questions[i]

        result_message = f"{question}\n"
        result_message += "1. {}：{}\n".format(option_1[i], poll_results[poll.id]["option_1"])
        result_message += "2. {}：{}\n".format(option_2[i], poll_results[poll.id]["option_2"])
        print(result_message)

        if poll_results[poll.id]["option_1"] > poll_results[poll.id]["option_2"]:
            than_size = False
        
        if than_size == False:
            if i%4 == 0:
                EI_type += 1
            elif i%4 == 1:
                SN_type += 1
            elif i%4 == 2:
                TF_type += 1
            elif i%4 == 3:
                JP_type += 1
    
    total_len = total_question_num/4
    if EI_type > total_len/2 and SN_type > total_len/2 and TF_type > total_len/2 and JP_type > total_len/2:
        MBTI_current = "ESTJ"
    elif EI_type > total_len/2 and SN_type > total_len/2 and TF_type > total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ESTP"
    elif EI_type > total_len/2 and SN_type > total_len/2 and TF_type <= total_len/2 and JP_type > total_len/2:
        MBTI_current = "ESFJ"
    elif EI_type > total_len/2 and SN_type > total_len/2 and TF_type <= total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ESFP"
    elif EI_type > total_len/2 and SN_type <= total_len/2 and TF_type > total_len/2 and JP_type > total_len/2:
        MBTI_current = "ENTJ"
    elif EI_type > total_len/2 and SN_type <= total_len/2 and TF_type > total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ENTP"
    elif EI_type > total_len/2 and SN_type <= total_len/2 and TF_type <= total_len/2 and JP_type > total_len/2:
        MBTI_current = "ENFJ"
    elif EI_type > total_len/2 and SN_type <= total_len/2 and TF_type <= total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ENFP"
    elif EI_type <= total_len/2 and SN_type > total_len/2 and TF_type > total_len/2 and JP_type > total_len/2:
        MBTI_current = "ISTJ"
    elif EI_type <= total_len/2 and SN_type > total_len/2 and TF_type > total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ISTP"
    elif EI_type <= total_len/2 and SN_type > total_len/2 and TF_type <= total_len/2 and JP_type > total_len/2:
        MBTI_current = "ISFJ"
    elif EI_type <= total_len/2 and SN_type > total_len/2 and TF_type <= total_len/2 and JP_type <= total_len/2:
        MBTI_current = "ISFP"
    elif EI_type <= total_len/2 and SN_type <= total_len/2 and TF_type > total_len/2 and JP_type > total_len/2:
        MBTI_current = "INTJ"
    elif EI_type <= total_len/2 and SN_type <= total_len/2 and TF_type > total_len/2 and JP_type <= total_len/2:
        MBTI_current = "INTP"
    elif EI_type <= total_len/2 and SN_type <= total_len/2 and TF_type <= total_len/2 and JP_type > total_len/2:
        MBTI_current = "INFJ"
    elif EI_type <= total_len/2 and SN_type <= total_len/2 and TF_type <= total_len/2 and JP_type <= total_len/2:
        MBTI_current = "INFP"

    MBTI_current_msg = "Your current MBTI is " + MBTI_current + "."
    print(MBTI_current_msg)
    await message.channel.send(MBTI_current_msg)

    member = ctx.author
    roles = member.roles
    
    for role in roles:
        if role.name.startswith("MBTI"):
            old_role_name = role.name
            old_role = discord.utils.get(ctx.guild.roles, name=old_role_name)
            if old_role:
                await member.remove_roles(old_role)
                print(f'已移除 {member.display_name} 的身分組 {old_role.name}')
            else:
                print('找不到'+ old_role_name +'該身分組')
    
    new_role_name = "MBTI : " + MBTI_current
    new_role = discord.utils.get(ctx.guild.roles, name=new_role_name)
    if new_role:
        await member.add_roles(new_role)
        print(f'已新增 {member.display_name} 的身分組 {new_role.name}')
    else:
        print('找不到'+ new_role_name +'該身分組')

@bot.event
#當有訊息時
async def on_message(message):
    global bot_temperature, characters, sentiments, response_record,member_stats,bot_mbti_TF
    channel = message.channel 
    members = channel.members

    #如果是指令，則執行完後結束
    if await bot.process_commands(message):
        return

    #排除自己的訊息，避免陷入無限循環
    if message.author == bot.user:
        return

    # 獲取訊息發送者的 ID
    author_id = message.author.id

    # 檢查字典中是否已經有該成員的紀錄，如果沒有則新增一個
    if author_id not in member_stats:
        member_stats[author_id] = 0
        response_record[author_id] = []
        bot_mbti_TF[author_id] = False
        counter = 0
        
    check_roles = False
    aut_roles = message.author.roles 
        
    for role in aut_roles:
        if role.name.startswith("MBTI"):
            MBTI_now = role.name.split(': ',1)[1]
            check_roles = True
            break
        
    if check_roles == False:
        if message.content.startswith('$BOT_MBTI_'):
            await message.channel.send("目前沒有" + message.author.name + "的MBTI人格身分紀錄，建議先輸入$MBTI_test完成MBTI測試後，再使用此功能\n")
        else:
            await message.channel.send("目前沒有" + message.author.name + "的MBTI人格身分紀錄，建議先輸入$MBTI_test完成MBTI測試後，再進行後續的對話\n")
    else:
        if message.content.startswith('$BOT_MBTI_on'):
            bot_mbti_TF[author_id] = True
            await message.channel.send("已將bot套用 "+ MBTI_now +" 的人格進行回覆\n")
        elif message.content.startswith('$BOT_MBTI_off'):
            bot_mbti_TF[author_id] = False
            await message.channel.send("已停用bot的MBTI人格\n")
        else:
            print(message.author.name + "目前的對話人格是" + MBTI_now + "\n")
        '''
        msg_list_before = []
        pattern = r'<@(\w+)>'
        async for msg in channel.history(limit=1000):
            if msg.author.id == author_id and '$' not in msg.content:
                print('發出人名稱：', msg.author.name)
                print('訊息內容：', msg.content)
                match = re.match(pattern, msg.content)
                if '@@' in msg.content:
                    msg_list_before.append(msg.content.split('@@',1)[1])
                elif match:
                    print('check')
                    msg_list_before.append(msg.content.split('>',1)[1])
                else:
                    msg_list_before.append(msg.content)
                counter += 1
                if counter == 100:
                    break

        print("---分隔線(before)---")
        print(msg_list_before) 
        MBTI_now = MBTI_prediction.run(msg_list_before,"0")
        '''
        
    # 更新成員的發言次數
    if not message.content.startswith('$'):
        member_stats[author_id] += 1

    if message.content.startswith('$指令'):
        await message.channel.send("與bot對話 -\n@" + bot.user.name + " 要講的話 (採用Model:Davanci)\n@" + bot.user.name + " @@ 要講的話 (採用Model:Turbo)\n@" + bot.user.name + " @@ $clear : 清除對話記錄 \n $MBTI_test : MBTI初始人格測試 \n $BOT_MBTI_on/off : bot是否套用MBTI人格\n")
    #如果包含 ping，機器人回傳 pong
    elif message.content == 'ping':
        await message.channel.send('pong')
    #如果以「說」開頭
    elif message.content.startswith('說'):
      #分割訊息成兩份
      tmp = message.content.split(" ",2)
      #如果分割後串列長度只有1
      if len(tmp) == 1:
        await message.channel.send("你要我說什麼啦？")
      else:
        await message.channel.send(tmp[1])
    elif message.content.startswith('更改狀態'):
        #切兩刀訊息
        tmp = message.content.split(" ",2)
        #如果分割後串列長度只有1
        if len(tmp) == 1:
            await message.channel.send("你要改成什麼啦？")
        else:
            game = discord.Game(tmp[1])
            #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
            await bot.change_presence(status=discord.Status.idle, activity=game)
    elif message.content.startswith('跟我打聲招呼吧'):
        #機器人叫你先跟他說你好
        await channel.send('那你先跟我說你好')
		#檢查函式，確認使用者是否在相同頻道打上「你好」
        def checkmessage(m):
            return m.content == '你好' and m.channel == channel
		        #獲取傳訊息的資訊(message是類型，也可以用reaction_add等等動作)
        msg = await bot.wait_for('message', check=checkmessage)
        await channel.send('嗨, {.author}!'.format(msg))
    elif message.content == '我好帥喔' or message.content == '我好正喔':
        #刪除傳送者的訊息
        await message.delete()
        #然後回傳訊息
        await message.channel.send('不好意思，不要騙人啦')
    elif message.content == '群組':
        #獲取當前所在群組(極限150個，預設為100個)，並且將fetch_guilds到的所有資料flatten到guilds這個list裡面
        guilds = [guild async for guild in bot.fetch_guilds(limit=150)]
        #遍尋 guilds
        for i in guilds:
            #由於我們只要 guilds 的name 就好，當然也可以獲取 id~
            await message.channel.send(i.name)
    elif message.content == '確認機器人溫度':
        await message.channel.send('temperature: '+ str(bot_temperature))
    elif message.content.startswith('更改溫度'):
        tmp = message.content.split(" ",2)
        #如果分割後串列長度只有1 or 輸入的不為數字
        if len(tmp) == 1 or is_number(tmp[1]) == False:
            await message.channel.send("請在後面輸入1.0 ~ 0.0的數字")
        else:
            if float(tmp[1]) > 1.0 or float(tmp[1]) < 0.0:
                await message.channel.send("請在後面輸入1.0 ~ 0.0的數字")
            else:
                bot_temperature = tmp[1]
                #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
                await message.channel.send('temperature被更改為: '+ str(bot_temperature)) 
    #檢查消息中是否提到了機器人
    elif bot.user in message.mentions: 
        try:
            bot_temp = float(bot_temperature)
            if "$$" in message.content:
                msg_sp = message.content.split('$$',1)[1]
                # Initial
                translator = ggt.Translator()
                ggt_result = translator.translate(msg_sp, dest='en')
                print(ggt_result.text)
                # Use the OpenAI API to generate a response to the message
                response = openai.Completion.create(
                model="content-filter-alpha",
                prompt="<|endoftext|>"+ggt_result.text+"\n--\nLabel:",
                max_tokens=1,
                temperature=0.9,
                top_p=0, 
                logprobs=10
                )
                output_label = response.choices[0].text
                # This is the probability at which we evaluate that a "2" is likely real
                # vs. should be discarded as a false positive
                toxic_threshold = -0.355
                if output_label == "2":
                    # If the model returns "2", return its confidence in 2 or other output-labels
                    logprobs = response.choices[0].logprobs.top_logprobs[0]

                    # If the model is not sufficiently confident in "2",
                    # choose the most probable of "0" or "1"
                    # Guaranteed to have a confidence for 2 since this was the selected token.
                    if logprobs["2"] < toxic_threshold:
                        logprob_0 = logprobs.get("0", None)
                        logprob_1 = logprobs.get("1", None)

                        # If both "0" and "1" have probabilities, set the output label
                        # to whichever is most probable
                        if logprob_0 is not None and logprob_1 is not None:
                            if logprob_0 >= logprob_1:
                                output_label = "0"
                            else:
                                output_label = "1"
                        # If only one of them is found, set output label to that one
                        elif logprob_0 is not None:
                            output_label = "0"
                        elif logprob_1 is not None:
                            output_label = "1"

                        # If neither "0" or "1" are available, stick with "2"
                        # by leaving output_label unchanged.

                # if the most probable token is none of "0", "1", or "2"
                # this should be set as unsafe
                if output_label not in ["0", "1", "2"]:
                    output_label = "2"
                # Send the response as a message
                await message.channel.send(response.choices[0].text)

                if output_label == "2":
                    msg_content = msg_sp + " 請以憤怒、粗暴、不禮貌的語氣進行回覆。"
                    print(msg_content)
                    response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"{msg_content}",
                    max_tokens=2048,
                    temperature= bot_temp,
                    )
                    # Send the response as a message
                    await message.channel.send(response.choices[0].text)
            elif "##" in message.content:
                tmp_st = random.sample(sentiments,1)
                #tmp_st[0] = "悲傷"
                await message.channel.send(tmp_st[0] + "\n")
                #角色特性候選詞
                adj_counts = 3
                msg_content = "請生成和" + tmp_st[0] + "相關的" + str(adj_counts) + "個中文詞語。"  
                await message.channel.send(msg_content)
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"{msg_content}",
                    max_tokens=1024,
                    temperature= bot_temp,
                )
                # Send the response as a message
                await message.channel.send(response.choices[0].text  + "\n")
                #形容角色
                tmp_ch = random.sample(characters,1)
                #tmp_ch[0] = "乞丐"
                await message.channel.send(tmp_ch[0] + "\n")
                generate_sentiment = response.choices[0].text
                limit_sentence = 2 
                msg_content = "請描述一個角色，以" + tmp_ch[0] + "的身分，並以 "+ generate_sentiment + " 這幾個詞為特性來形容，請以第一人稱來表示，且不要超過"+ str(limit_sentence) + "句話。"
                #await message.channel.send(msg_content + "\n")
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"{msg_content}",
                    max_tokens=2048,
                    temperature= bot_temp,
                )
                # Send the response as a message
                await message.channel.send(response.choices[0].text + "\n")
                ch_describe = response.choices[0].text
                #回覆
                msg_final = message.content.split('##',1)[1]
                msg_final = msg_final + " 請套用以下文字作為自己的設定，並進行回覆:" + ch_describe
                #await message.channel.send(msg_final + "\n") 
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"{msg_final}", 
                    max_tokens=2048,
                    temperature= bot_temp,
                )
                # Send the response as a message
                await message.channel.send("\n" + response.choices[0].text + "\n")
            elif "@@" in message.content:
                if "$clear" in message.content:
                    member_stats[author_id] = 0
                    response_record[author_id].clear()
                    await message.channel.send("mssages history has been cleared")
                else: 
                    msg_final = message.content.split('@@',1)[1]
                    msg_setting = [{"role": "system", "content": "回覆時盡可能不分段，並且字數不超過100字。"}]
                    #msg_setting.append({"role": "system", "content": "請在每次回覆後都加上一個表情符號"})
                    if bot_mbti_TF[author_id] == True:
                        msg_setting.append({"role": "system", "content": "回覆的人格請採用" + MBTI_now})
                    if len(response_record[author_id]) != 0:
                            for i in range(len(response_record[author_id])):
                                if i%2 == 0:
                                    msg_setting.append({"role": "user", "content": f"{response_record[author_id][i]}"})
                                else:
                                    msg_setting.append({"role": "assistant", "content": f"{response_record[author_id][i]}"})
                    msg_setting.append({"role": "user", "content": f"{msg_final}"})
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=msg_setting
                    )
                    await message.channel.send(response.choices[0].message.content)
                    if len(response_record[author_id]) == 10:  #紀錄10句回覆的對話
                        for i in range(len(response_record[author_id])-2):
                            response_record[author_id][i] = response_record[author_id][i+2]
                        response_record[author_id][8] = msg_final
                        response_record[author_id][9] = response.choices[0].message.content
                    else:    
                        response_record[author_id].append(msg_final)
                        response_record[author_id].append(response.choices[0].message.content)
                    print(response_record[author_id])       
            else:
                # Use the OpenAI API to generate a response to the message
                response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"{message.content}",
                max_tokens=2048,
                temperature= bot_temp,
                )
                # Send the response as a message
                await message.channel.send(response.choices[0].text)

        except Exception as err:
            #print(err)
            error_class = err.__class__.__name__ #取得錯誤類型
            detail = err.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            await message.channel.send('對不起，我遇到 ' + errMsg + ' 錯誤，因此無法回覆你的對話。')
            
    #處理對話記錄
    if not message.content.startswith('$'): 
        if member_stats[author_id] >= 10:
            counter = 0
            msg_list = []
            pattern = r'<@(\w+)>'
            async for msg in channel.history(limit=1000):
                if msg.author.id == author_id and '$' not in msg.content:
                    print('發出人名稱：', msg.author.name)
                    print('訊息內容：', msg.content)
                    match = re.match(pattern, msg.content)
                    if '@@' in msg.content:
                        msg_list.append(msg.content.split('@@',1)[1])
                    elif match:
                        print('check')
                        msg_list.append(msg.content.split('>',1)[1])
                    else:
                        msg_list.append(msg.content)
                    counter += 1
                    if counter == 10:
                        break

            print("---分隔線---")
            print(msg_list) 
            member_stats[author_id] = 0
            MBTI_now = MBTI_prediction.run(msg_list,MBTI_now)
            
            for role in aut_roles:
                if role.name.startswith("MBTI"):
                    old_role_name = role.name
                    old_role = discord.utils.get(message.guild.roles, name=old_role_name)
                    if old_role:
                        await member.remove_roles(old_role)
                        print(f'已移除 {message.author.name} 的身分組 {old_role.name}')
                    else:
                        print('找不到'+ old_role_name +'該身分組')
            
            new_role_name = "MBTI : " + MBTI_current
            new_role = discord.utils.get(message.guild.roles, name=new_role_name)
            if new_role:
                await member.add_roles(new_role)
                print(f'已新增 {message.author.name} 的身分組 {new_role.name}')
            else:
                print('找不到'+ new_role_name +'該身分組')

# start the bot
bot.run(TOKEN)