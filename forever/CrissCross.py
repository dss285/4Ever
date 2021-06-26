import discord
import re
import asyncio
from models.EmbedTemplate import EmbedTemplate
class CrissCross:
# x x x
# x x x
# x x x
    def __init__(self, player1, player2, client, size=3):
        self.map = self.Map(size)
        self.player1 = (player1, 'x')
        self.player2 = (player2, '0')
        self.client = client
        self.turn = 1
    async def StartGame(self, channel):
        async def getResponse(player, next_turn):
            response = await self.client.wait_for('message', timeout=30.0, check=lambda x: x.author == player[0] and channel == x.channel)
            self.turn = next_turn
            return response
        def runResponse(player, response):
            reg = re.match(r"(\w{1})(\d{1,2})", response.content)
            if reg:
                row = reg.group(1).lower()
                column = int(reg.group(2))
                value = player[1]
                if not self.map.setValue(row, column, value):
                    return False
                return True
                
        breakloop = False
        while not self.map.gameOver():
            if self.map.mapFilled():
                await channel.send(":necktie:")
                return
            await channel.send(embed=self.getEmbed())
            if self.turn == 1:
                try:
                    await channel.send(f"> {self.player1[0].mention}, your turn")
                    response = await getResponse(self.player1, 2)
                    if not runResponse(self.player1, response):
                        self.turn = 1
                        await channel.send("Wrong input, try again")
                        continue
                except asyncio.TimeoutError:
                    await channel.send("> Game over, other player did not respond in time.")
                    breakloop = True
            else:
                try:
                    await channel.send(f"{self.player2[0].mention}, your turn")
                    response = await getResponse(self.player2, 1)
                    if not runResponse(self.player2, response):
                        self.turn = 2
                        await channel.send("Wrong input, try again")
                        continue
                except asyncio.TimeoutError:
                    await channel.send("> Game over, other player did not respond in time.")
                    breakloop = True
            
            if breakloop:
                break
        if self.turn == 2: #player1 won
            await channel.send(f"> {self.player1[0].mention} won")
        elif self.turn==1:
            await channel.send(f"> {self.player2[0].mention} won")
    def getEmbed(self,):
        em = EmbedTemplate(title="Crisscross", description=f"{self.player1[0].mention} :x: vs {self.player2[0].mention} :o:")
        em.add_field(name="Game", value=str(self.map).replace("x", ":x:").replace("0", ":o:").replace("-", ":large_blue_diamond:"))
        return em
    class Map:
        def __init__(self, size = 3):
            self.map = {}
            
            for i in 'abcdefghijklmnopqrstuvwxyz':
                if len(self.map) < size:
                    tmp = []
                    for j in range(size):
                        tmp.append("-")
                    self.map[i] = tmp
                else:
                    break
        def mapFilled(self,):
            for i in self.map:
                if "-" in self.map[i]:
                    return False
            return True
        def gameOver(self,):
            # X - X - X
            for i in self.map:
                val = None
                loopbroke = False
                for j in self.map[i]:
                    if j == "-":
                        loopbroke = True
                        break

                    if val == None:
                        val = j
                    else:
                        if not val == j:
                            loopbroke = True
                            break
                if not loopbroke:
                    return True
            # X
            # X
            # X
            for j in range(len(self.map)):
                val = None
                loopbroke = False
                for i in self.map:
                    if self.map[i][j] == "-":
                        loopbroke = True
                        break
                    if val == None:
                        val = self.map[i][j]
                    else:
                        if not val == self.map[i][j]:
                            loopbroke = True
                            break
                if not loopbroke:
                    return True


            #X
            # X
            #  X
            val = None
            x = 0
            loopbroke = False
            for i in self.map:
                if self.map[i][x] == "-":
                    loopbroke = True
                    break
                if val == None:
                    val = self.map[i][x]
                else:
                    if not val == self.map[i][x]:
                        loopbroke = True
                        break
                x = x+1
            if not loopbroke:
                return True
            #  X
            # X
            #X
            loopbroke = False
            x = len(self.map)-1
            for i in self.map:
                if self.map[i][x] == "-":
                    loopbroke = True
                    break
                if val == None:
                    val = self.map[i][x]
                else:
                    if not val == self.map[i][x]:
                        loopbroke = True
                        break
                x = x-1
            if not loopbroke:
                return True
            return False
        def setValue(self, row, column, value):
            column -= 1
            if column >= len(self.map.keys()):
                column = len(self.map.keys())-1
            elif column < 0:
                column = 0
            if self.map[row][column] == "-":
                self.map[row][column] = value
                return True
            else:
                return False
        def __str__(self,):
            convert = ""
            for i in self.map:
                convert += " ".join(self.map[i])+"\n"
            return convert

if __name__ == "__main__":
    mappi = CrissCross.Map()
    print(mappi)
    mappi.setValue('a', 1, "X")
    mappi.setValue('a', 2, "X")
    mappi.setValue('a', 3, "X")
    mappi.setValue('b', 2, "X")
    print(mappi)
    print(mappi.gameOver())