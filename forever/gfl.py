import discord
import operator
import asyncio
import re
import forever.database
import datetime
class girlsfrontline:
    def __init__(self, database):
        self.db = database
        self.replacelist = {
            "suppressor" : [
                "supp"
            ],
            "telescopic sight" : [
                "tele",
                "ts"
            ],
            "holographic sight" : [
                "holo",
                "hs"
            ],
            "exoskeleton" : [
                "exo"
            ],
            "night combat equipment" : [
                "night",
                "nce"
            ],
            "red dot sight" : [
                "rd", 
                "reddot"
            ],
            "hollow point ammo" : [
                "hp"
            ],
            "shotgun ammo" : [
                "shotgun"
            ],
            "camouflage cape" :[
                "cg"
            ],
            "high velocity ammo" : [
                "hv",
                "hvammo"
            ],
            "ap ammo" : [
                "ap",
                "apammo"
            ],
            "armor plate" : [
                "armor",
                "aplate"
            ],
            "ammo box" : [
                "ammobox",
                "ab",
                "ammob"
            ]
        }
    
    async def parse(self, message, key):
        reg = re.match(key+"gfl\s(productiontimers)\s?(.*)?", message.content)
        everythingok = False
        if reg:
            if reg.group(1):
                if reg.group(2):
                    if reg.group(1) in ["productiontimers"]:
                        reg_2 = re.match("(.*)\s(.*)",reg.group(2))
                        if reg_2:
                            if reg.group(1) == "productiontimers":
                                if reg_2.group(1) in ["eq", "equipment","doll","tdoll","waifu"]:
                                    prodtype = "equipment" if reg_2.group(1) in ["eq", "equipment"] else "tdoll"
                                    splitted = reg_2.group(2).lower()
                                    everythingok = True
                                    
                                    for i in [":", "|", ",", "-"]:
                                        if i in splitted:
                                            splitted = splitted.split(i)
                                    tmp = []
                                    if type(splitted) == list:
                                        for i in splitted:
                                            if prodtype == "tdoll":
                                                if i in ["ar","rf","sg","mg","hg","smg"]:
                                                    print("ok")
                                                    tmp.append(i)
                                            elif prodtype == "equipment":
                                                tmp.append(self.replacer(i))
                                    else:
                                        if prodtype == "tdoll" and splitted in ["ar","rf","sg","mg","hg","smg"]:
                                            tmp = splitted
                                        elif prodtype =="equipment":
                                            tmp = self.replacer(splitted)
                                    if everythingok and tmp:
                                    
                                        await self.productionTimers(message.channel, prodtype, tmp)
                                    
                                    else:
                                    
                                        everythingok = False

        return everythingok
    def replacer(self, replaced):
        for j,k in self.replacelist.items():
            if replaced in k:
                replaced = j
                break
        return replaced
    async def productionTimers(self, channel, prodtype, subtype):
        em = discord.Embed(title="Production Timers", description=prodtype.title()+" production timers", color=0x8A00E0)
        if type(subtype) == list:
            for s in subtype:
                self.prdtimer(em, prodtype, s)
        else:
            self.prdtimer(em, prodtype, subtype)
        await channel.send(embed=em)
        
        
    def prdtimer(self, em, prodtype, s):

        tmp = ""
        if prodtype == "tdoll":
            for x in sorted(self.db["gfl"]["productiontimers"][prodtype][s], key=lambda x: x.count("⭐")):
                tmp = tmp+"\n\n**"+x.title()+"**\n"
                for i, j in sorted(self.db["gfl"]["productiontimers"][prodtype][s][x].items(), key=lambda x: x[1]):
                    tmp = tmp+i+" - "+str(datetime.timedelta(seconds=j))+"\n"
            em.add_field(name=s.upper(),value=tmp)
        elif prodtype == "equipment":
            for x,y in sorted(self.db["gfl"]["productiontimers"][prodtype][s].items(),key=lambda x: len(x[0])):
                tmp = tmp+"\n\n**"+x.title()+"**\n"
                if s in ["shotgun ammo", "exoskeleton"]:
                    for i, j in sorted(y.items(),key=lambda x: x[0].count("⭐")):
                        tmp = tmp+i+" - "+str(datetime.timedelta(seconds=j))+"\n"
                else:
                    tmp = tmp+str(datetime.timedelta(seconds=y))+"\n"
            em.add_field(name=s.upper(), value=tmp)





