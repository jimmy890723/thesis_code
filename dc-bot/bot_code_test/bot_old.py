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

# Set up the OpenAI API client
openai.api_key = OPENAI_KEY

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

bot_temperature = 0.5

characters = [ "酸民" , "正義人士" , "警察" , "囚犯" , "學生" , "導演" , "乞丐" , "歌手" , "愛國人士" , "外星人" , "和尚" ] 

sentiments = [ "喜悅" , "憤怒" , "悲傷" , "恐懼" , "厭惡" , "驚奇" , "羨慕" , "羞怯" ]

response_record = []

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  game = discord.Game('測試用機器人，輸入"$指令"查看功能')
  #discord.Status.<狀態>，可以是online,offline,idle,dnd,invisible
  await client.change_presence(status=discord.Status.idle, activity=game)
  
  
@client.event
#當有訊息時
async def on_message(message):
    global bot_temperature, characters, sentiments, response_record
    #排除自己的訊息，避免陷入無限循環
    if message.author == client.user:
        return
    elif message.content.startswith('$指令'):
        await message.channel.send("與bot對話 -\n@" + client.user.name + " 要講的話 (採用Model:Davanci)\n@" + client.user.name + " @@ 要講的話 (採用Model:Turbo)\n@" + client.user.name + " @@ !clear : 清除對話記錄 \n")
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
            await client.change_presence(status=discord.Status.idle, activity=game)
    elif message.content.startswith('跟我打聲招呼吧'):
        channel = message.channel
        #機器人叫你先跟他說你好
        await channel.send('那你先跟我說你好')
		#檢查函式，確認使用者是否在相同頻道打上「你好」
        def checkmessage(m):
            return m.content == '你好' and m.channel == channel
		        #獲取傳訊息的資訊(message是類型，也可以用reaction_add等等動作)
        msg = await client.wait_for('message', check=checkmessage)
        await channel.send('嗨, {.author}!'.format(msg))
    elif message.content == '我好帥喔' or message.content == '我好正喔':
        #刪除傳送者的訊息
        await message.delete()
        #然後回傳訊息
        await message.channel.send('不好意思，不要騙人啦')
    elif message.content == '群組':
        #獲取當前所在群組(極限150個，預設為100個)，並且將fetch_guilds到的所有資料flatten到guilds這個list裡面
        guilds = [guild async for guild in client.fetch_guilds(limit=150)]
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
    elif client.user in message.mentions: 
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
                if "!clear" in message.content:
                    response_record.clear()
                    await message.channel.send("mssages history has been cleared")
                else: 
                    msg_final = message.content.split('@@',1)[1]
                    msg_setting = [{"role": "system", "content": "回覆的對話不能超過20個字"}]
                    if len(response_record) != 0:
                            for i in range(len(response_record)):
                                if i%2 == 0:
                                    msg_setting.append({"role": "user", "content": f"{response_record[i]}"})
                                else:
                                    msg_setting.append({"role": "assistant", "content": f"{response_record[i]}"})
                    msg_setting.append({"role": "user", "content": f"{msg_final}"})
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=msg_setting
                    )
                    await message.channel.send(response.choices[0].message.content)
                    if len(response_record) == 10:
                        for i in range(len(response_record)-2):
                            response_record[i] = response_record[i+2]
                        response_record[8] = msg_final
                        response_record[9] = response.choices[0].message.content
                    else:    
                        response_record.append(msg_final)
                        response_record.append(response.choices[0].message.content)
                    print(response_record)       
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

# start the bot
client.run(TOKEN)