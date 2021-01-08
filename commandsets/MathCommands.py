
import asyncio
import discord

from abstract.EmbedTemplate import EmbedTemplate
from abstract.Commands import Commands
from abstract.Command import Command

from forever.Math import Math

import math
class MathCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client):
        self.client = client
        commandList = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandList, description, commandKey)
    def fetchCommands(self, commandKey):
        commandList = {}
        commandList["probability"] = Probability(commandKey, self.client)
        return commandList
class Probability(Command):
    def __init__(self, commandKey, client):
        self.client = client
        super().__init__(commandKey, "probability", """Calculates probability""", "{} {}".format(commandKey, "probability"), ["chances"])
    async def run(self, message, server):
        def is_number(s):
            try:
                float(s.content)
                return True
            except ValueError:
                return False
        try:
            await message.channel.send(embed=EmbedTemplate(title="Probability", description="Amount of trials"))
            trials = await self.client.wait_for('message', timeout=30.0, check=is_number)
            await message.channel.send(embed=EmbedTemplate(title="Probability", description="Chance (in %)"))
            chance = await self.client.wait_for('message', timeout=30.0, check=is_number)
            await message.channel.send(embed=EmbedTemplate(title="Probability", description="Wanted amount of successes"))
            successes = await self.client.wait_for('message', timeout=30.0, check=is_number)
            if trials and chance and successes:
                successes = float(successes.content)
                trials = float(trials.content)
                chance = float(chance.content)/100

                em = EmbedTemplate(title='Probability', description="Calculated probability")
                em.add_field(name="Trials", value="{}".format(trials))
                em.add_field(name="Successes", value="{}".format(successes))
                em.add_field(name="Chance", value="{}".format(chance))
                em.add_field(name="Probability", value="{}".format(
                                Math.probability(trials, 
                                                    successes, chance)))
                await message.channel.send(embed=em)
        except asyncio.TimeoutError:
            await message.channel.send(embed=EmbedTemplate(title="Probability", description="Timed out"))