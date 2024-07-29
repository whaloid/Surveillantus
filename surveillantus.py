# インストールした discord.py を読み込む
import discord
import json
import os
from openai import OpenAI
import requests
import random
import re
import time
from discord.ext import tasks
from datetime import datetime as dt
from datetime import timedelta
from discord import app_commands

class Surveillantus:
    def __init__(self,json_pref):
        with open(json_pref,'r') as f:
            self.settings=json.load(f)
        self.discord_token=self.settings["discord_token"]
        with open(self.settings['roleplay'], 'r') as f:
            self.roleplay=f.read()
        with open(self.settings['question_example'],"r") as f:
            self.question_example=f.read()
        with open(self.settings["helpdoc"],"r") as f:
            self.helpdoc=f.read()

        self.messages=[]
        self.messages.append({"role":"system","content":self.roleplay})
        self.gpt_client=OpenAI(api_key=self.settings["openai_api_key"])

        self.endpoint=self.settings["endpoint"]
    
    #投稿のリストからギルド、チャンネル、ユーザの情報を得る
    def js02gcus(self,js0):
        guilds={}
        channels={}
        users={}
        for post in js0["posts"]:
            if not (post["guild_id"] in guilds):
                jsg=requests.get(self.endpoint,
                                    params={"operation":"id2serv",
                                            "guild_id":post["guild_id"]}).json()
                if len(jsg["guilds"])>0:
                    guilds[post["guild_id"]]=jsg["guilds"][0]["guild_name"]
                else:
                    guilds[post["guilds_id"]]="GUILDID:{}".format(post["guild_id"])
        for post in js0["posts"]:
            if not (post["channel_id"] in channels):
                jsg=requests.get(self.endpoint,
                                    params={"operation":"id2chan",
                                            "channel_id":post["channel_id"]}).json()
                if len(jsg["channels"])>0:
                    channels[post["channel_id"]]=jsg["channels"][0]["channel_name"]
                else:
                    channels[post["channel_id"]]="CHANNELID:{}".format(post["channel_id"])
        for post in js0["posts"]:
            if not (post["user_id"] in users):
                jsg=requests.get(self.endpoint,
                                    params={"operation":"id2user",
                                            "user_id":post["user_id"]}).json()
                if len(jsg["users"])>0:
                    users[post["user_id"]]=jsg["users"][0]["disp_name"]
                else:
                    users[post["user_id"]]="USERID:{}".format(post["user_id"])
        return guilds,channels,users
    
    def run(self):
        # 接続に必要なオブジェクトを生成
        Intents = discord.Intents.all()
        Intents.members = True
        global client
        client = discord.Client(intents=Intents)
        global tree
        tree = app_commands.CommandTree(client)

        # 起動時に動作する処理
        @client.event
        async def on_ready():
            # 起動したらターミナルにログイン通知が表示される
            await tree.sync()
            print('logged in')

        @tree.command(name="chat",description="Surveillantusと会話できます。")
        async def chat(interaction: discord.Interaction, question:str):
            await interaction.response.defer(thinking=True)
            #メッセージ履歴が10を超えたらユーザとBotのメッセージを1つずつ消す。
            #ユーザ別の保持はサポートしない。
            if len(self.messages)>=10:
                self.messages.pop(1)
                self.messages.pop(1)
            self.messages.append(
                {"role":"user","content":question}
            )
            completion = self.gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages
            )
            answer=completion.choices[0].message.content
            answer_=completion.choices[0].message
            self.messages\
            .append({"role":answer_.role,"content":answer_.content})

            embed0 = discord.Embed( # Embedを定義する
                    title="",# タイトル
                    color=0xffffff, # フレーム色指定(今回は緑)
                    #description="女神Artiphiusがあなたに答えています。", # Embedの説明文 必要に応じて
                    )
            embed0.add_field(name="Surveillantusの神託",value="**{}**".format(answer)) # フィールドを追加。
            embed0.add_field(name="質問例",value=self.question_example)

            await interaction.followup.send("",embed=embed0)
        @tree.command(name="mes_word",description="指定された語句を含むメッセージを検索できます。")
        async def mes_word(interaction:discord.Interaction,word:str):
            await interaction.response.defer(thinking=True)
            js0=requests.get(self.endpoint,
                params={"operation":"word2mes","word":word}).json()
            guilds,channels,users=self.js02gcus(js0)
            text=""
            rid=str(random.randint(0,100)).zfill(3)
            f=open("results{}.txt".format(rid),"w")
            if len(js0["posts"])>=100:
                js0["posts"]=js0["posts"][0:100]
            for post in js0["posts"]:
                text="server:{},\nchannel:,{}\nuser:{},\ncontent:{},\ntime:{},\n\n"\
                .format(guilds[post["guild_id"]],channels[post["channel_id"]],
                        users[post["user_id"]],post["content"],post["time"])
                f.write(text)
            f.close()
            await interaction.followup.send("{}の検索結果(MESSAGE):\n"
                                        .format(word),
                                        file=discord.File("results{}.txt".format(rid)))
            os.remove("results{}.txt".format(rid))
        
        @tree.command(name="gld_word",description="語句に関連するサーバを検索します。")
        async def gld_word(interaction:discord.Interaction,word:str):
            await interaction.response.defer(thinking=True)
            js0=requests.get(self.endpoint,
                params={"operation":"word2serv","word":word}).json()
            tex0=""
            f=open("servers_{}.txt".format(word),"w")
            for guild in js0["guilds"]:
                tex0="id:{},\nname:,{}\n\n"\
                .format(guild["guild_id"],guild["guild_name"])
                f.write(tex0)
            f.close()
            await interaction.followup.send("{}の検索結果(SERVER):\n"
                                        .format(word),
                                        files=[
                                            discord.File("servers_{}.txt".format(word)),
                                        ])
            time.sleep(1)
            os.remove("servers_{}.txt".format(word))
        @tree.command(name="ch_word",description="語句からチャンネルを検索します。")
        async def ch_word(interaction:discord.Interaction,word:str):
            await interaction.response.defer(thinking=True)
            js1=requests.get(self.endpoint,
                params={"operation":"word2chan","word":word}).json()
            tex1=""
            f=open("channels_{}.txt".format(word),"w")
            for channel in js1["channels"]:
                tex1="id:{},\nname:,{}\ntopic:,{}\n\n"\
                .format(channel["channel_id"],
                        channel["channel_name"],
                        channel["channel_topic"])
                f.write(tex1)
            f.close()

            await interaction.followup.send("{}の検索結果(CHANNEL):\n"
                                        .format(word),
                                        files=[
                                            discord.File("channels_{}.txt".format(word))
                                        ])
            time.sleep(1)
            os.remove("channels_{}.txt".format(word))
        
        @tree.command(name="usr_word",description="語句からユーザを探します。表示名、ユーザ名に対応")
        async def usr_word(interaction:discord.Interaction,word:str):
            await interaction.response.defer(thinking=True)
            js2=requests.get(self.endpoint,
                params={"operation":"word2user","word":word}).json()
            tex2=""
            f=open("users_{}.txt".format(word),"w")
            for user in js2["users"]:
                tex2="id:{},\nuser_name:,{}\ndisp_name:,{}\n\n"\
                .format(user["user_id"],
                        user["user_name"],
                        user["disp_name"])
                f.write(tex2)
            f.close()

            await interaction.followup.send("{}の検索結果(USER):\n"
                                        .format(word),
                                        files=[
                                            discord.File("users_{}.txt".format(word))
                                        ])
            time.sleep(1)
            os.remove("users_{}.txt".format(word))
        @tree.command(name="mes_usr",description="語句かIDに関連したユーザの発言を一括取得できます。")
        async def mes_usr(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*19),arg))==1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"user2mes",
                    "user_id":arg
                }).json()
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2user",
                        "word":arg
                    }).json()
                userids=[user["user_id"] for user in js0["users"]]
                js0={"posts":[]}
                for userid in userids:
                    js0_=requests.get(self.endpoint,params={
                        "operation":"user2mes",
                        "user_id":userid
                    }).json()
                    js0["posts"]=js0["posts"]+js0_["posts"]
            guilds,channels,users=self.js02gcus(js0)
            tex=""
            f=open("results_{}.txt".format(arg),"w")
            for post in js0["posts"]:
                tex="server:{},\nchannel:,{}\nuser:{},\ncontent:{},\ntime:{},\n\n"\
                .format(guilds[post["guild_id"]],channels[post["channel_id"]],
                        users[post["user_id"]],post["content"],post["time"])
                f.write(tex)
            f.close()

            await interaction.followup.send("{}の検索結果(USER2MESSAGE):\n"
                                        .format(arg),
                                        file=discord.File("results_{}.txt".format(arg)))
            os.remove("results_{}.txt".format(arg))
        @tree.command(name="mes_ch",description="語句に関連したチャンネルのメッセージを一括取得できます。")
        async def mes_ch(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*15),arg))>=1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"chan2mes",
                    "channel_id":arg
                }).json()
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2chan",
                        "word":arg
                    }).json()
                channelids=[channel["channel_id"] for channel in js0["channels"]]
                js0={"posts":[]}
                if len(channelids)>0:
                    js0["posts"]=requests.get(self.endpoint,params={
                        "operation":"chan2mes",
                        "channel_id":channelids[random.randint(0,len(channelids)-1)]
                    }).json()
            guilds,channels,users=self.js02gcus(js0)
            tex=""
            f=open("posts_{}.txt".format(arg),"w")
            for post in js0["posts"]:
                tex="server:{},\nchannel:,{}\nuser:{},\ncontent:{},\ntime:{},\n\n"\
                .format(guilds[post["guild_id"]],channels[post["channel_id"]],
                        users[post["user_id"]],post["content"],post["time"])
                f.write(tex)
            f.close()

            await interaction.followup.send("{}の検索結果(USER2MESSAGE):\n"
                                        .format(arg),
                                        file=discord.File("posts_{}.txt".format(arg)))
            os.remove("posts_{}.txt".format(arg))
        @tree.command(name="mem_gld",description="語句かIDに関連するサーバのメンバー一覧を取得します。")
        async def mem_gld(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*15),arg))>=1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"serv2user",
                    "guild_id":arg
                }).json()
                gnjs=requests.get(self.endpoint,params={
                    "operation":"id2serv",
                    "guild_id":arg
                }).json()
                for user in js0["users"]:
                    if len(gnjs["guilds"])>0:
                        user["guild_name"]=gnjs["guilds"][0]["guild_name"]
                    else:
                        user["guild_name"]="Not Found."
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2serv",
                        "word":arg
                    }).json()
                guildids=[guild["guild_id"] for guild in js0["guilds"]]
                js1={"users":[]}
                for guildid in guildids:
                    js1_=requests.get(self.endpoint,params={
                        "operation":"serv2user",
                        "guild_id":guildid
                    }).json()
                    for user in js1_["users"]:
                        targname="Not Found."
                        for guild in js0["guilds"]:
                            if guildid==guild["guild_id"]:
                                targname=guild["guild_name"]
                        user["guild_name"]=targname
                    js1["users"]=js1["users"]+js1_["users"]
                js0=js1
                
            tex=""
            f=open("members_{}.txt".format(arg),"w")
            for user in js0["users"]:
                tex="server:{},\nuser_name:,{}\ndisp_name:{},\n\n"\
                .format(user["guild_name"],user["user_name"],
                        user["disp_name"])
                f.write(tex)
            f.close()
            await interaction.followup.send("{}の検索結果(SERV2CHAN):\n"
                                        .format(arg),
                                        file=discord.File("members_{}.txt".format(arg)))
            os.remove("members_{}.txt".format(arg))
        @tree.command(name="ch_gld",description="語句かIDに関連したサーバのチャンネル一覧を取得できます。")
        async def ch_gld(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*15),arg))>=1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"serv2chan",
                    "guild_id":arg
                }).json()
                gnjs=requests.get(self.endpoint,params={
                    "operation":"id2serv",
                    "guild_id":arg
                }).json()
                for channel in js0["channels"]:
                    if len(gnjs["guilds"])>0:
                        channel["guild_name"]=gnjs["guilds"][0]["guild_name"]
                    else:
                        channel["guild_name"]="Not Found."
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2serv",
                        "word":arg
                    }).json()
                guildids=[guild["guild_id"] for guild in js0["guilds"]]
                js1={"channels":[]}
                for guildid in guildids:
                    js1_=requests.get(self.endpoint,params={
                        "operation":"serv2chan",
                        "guild_id":guildid
                    }).json()
                    for channel in js1_["channels"]:
                        targname="Not Found."
                        for guild in js0["guilds"]:
                            if guildid==guild["guild_id"]:
                                targname=guild["guild_name"]
                        channel["guild_name"]=targname
                    js1["channels"]=js1["channels"]+js1_["channels"]
                js0=js1
                
            tex=""
            f=open("channels_{}.txt".format(arg),"w")
            for channel in js0["channels"]:
                tex="server:{},\nchannel:,{}\ntopic:{},\n\n"\
                .format(channel["guild_name"],channel["channel_name"],
                        channel["channel_topic"])
                f.write(tex)
            f.close()
            await interaction.followup.send("{}の検索結果(SERV2CHAN):\n"
                                        .format(arg),
                                        file=discord.File("channels_{}.txt".format(arg)))
            os.remove("channels_{}.txt".format(arg))
        @tree.command(name="sum_ch",description="語句かIDに関連するチャンネルを要約します。")
        async def sum_ch(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*15),arg))>=1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"chan2mes",
                    "channel_id":arg
                }).json()
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2chan",
                        "word":arg
                    }).json()
                channelids=[channel["channel_id"] for channel in js0["channels"]]
                js0={"posts":[]}
                if len(channelids)>0:
                    idx=random.randint(0,len(channelids)-1)
                    js0=requests.get(self.endpoint,params={
                        "operation":"chan2mes",
                        "channel_id":channelids[idx]
                    }).json()
            guilds,channels,users=self.js02gcus(js0)
            prompt="以下のDiscordログを要約してください。ただし、入力形式は (author:<ユーザ名>, content:<内容>, time:<投稿時刻>)となっています。出力形式は自由です。\n"
            for post in js0["posts"]:
                s="(author:{}, content:{}, time:{})\n"\
                .format(users[post["user_id"]], post["content"], post["time"])
                prompt=prompt+s
                if len(list(prompt))>=5000:
                    break
            
            completion = self.gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":prompt}]
            )
            answer=completion.choices[0].message.content
            if len(list(answer))>2000:
                answer=answer[0:2000]
            await interaction.followup.send("**要約結果：**\n{}".format(answer))
        
        @tree.command(name="sum_usr",description="語句かIDに関連するユーザの発言を要約します。")
        async def sum_usr(interaction:discord.Interaction,arg:str):
            await interaction.response.defer(thinking=True)
            if len(re.findall("({})".format("\d"*19),arg))==1:
                mode="id"
            else:
                mode="name"
            if mode=="id":
                js0=requests.get(self.endpoint,params={
                    "operation":"user2mes",
                    "user_id":arg
                }).json()
            elif mode=="name":
                js0=requests.get(self.endpoint,
                    params={
                        "operation":"word2user",
                        "word":arg
                    }).json()
                userids=[user["user_id"] for user in js0["users"]]
                js0={"posts":[]}
                for userid in userids:
                    js0_=requests.get(self.endpoint,params={
                        "operation":"user2mes",
                        "user_id":userid
                    }).json()
                    js0["posts"]=js0["posts"]+js0_["posts"]
            guilds,channels,users=self.js02gcus(js0)
            prompt="以下のDiscordログを要約してください。ただし、形式は (author:<ユーザ名>, content:<内容>, time:<投稿時刻>)となっています。\n"
            for post in js0["posts"]:
                s="(author:{}, content:{}, time:{})\n"\
                .format(users[post["user_id"]], post["content"], post["time"])
                prompt=prompt+s
                if len(list(prompt))>=5000:
                    break
            
            completion = self.gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":prompt}]
            )
            answer=completion.choices[0].message.content
            if len(list(answer))>2000:
                answer=answer[0:2000]
            await interaction.followup.send("**要約結果：**\n{}".format(answer))
        @tree.command(name="help",description="ヘルプを表示します。")
        async def help(interaction:discord.Interaction):
            await interaction.response.defer(thinking=True)
            await interaction.followup.send(self.helpdoc,ephemeral=True)
            
        # Botの起動とDiscordサーバーへの接続
        try:
            client.run(self.discord_token)
        except:
            os.system("kill 1")