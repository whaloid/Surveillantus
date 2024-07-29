import selfcord
import requests
from selfcord.ext import tasks
import os

class SpyClient(selfcord.Client):
    def __init__(self,endpoint,**kwargs):
        super().__init__(**kwargs)
        self.endpoint=endpoint

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message:selfcord.Message):
        # only respond to ourselves
        guild_id=message.guild.id
        channel_id=message.channel.id
        user_id=message.author.id
        post_id=message.id
        time=message.created_at
        content=message.content
        guild_name=message.guild.name
        channel_name=message.channel.name
        user_name=message.author.name
        disp_name=message.author.global_name
        channel_topic=message.channel.topic                
        time_="{}-{}-{} {}:{}:{}".format(
            time.year,time.month,time.day,
            time.hour,time.minute,time.second
        )
        requests.post(self.endpoint,
              data={
                  "guild_id":guild_id,
                  "channel_id":channel_id,
                  "user_id":user_id,
                  "post_id":post_id,
                  "guild_name":guild_name,
                  "channel_name":channel_name,
                  "channel_topic":channel_topic,
                  "user_name":user_name,
                  "disp_name":disp_name,
                  "time":time_,
                  "content":content
              })
        #with open("log.txt","a") as f:
        #    f.write(content)