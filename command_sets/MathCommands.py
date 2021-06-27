
import asyncio
import discord

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Utilities import Args
from forever import Math
class MathCommands(Commands):
    def __init__(self, module_name, description, command_key, client):
        self.client = client
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetch_commands(self, command_key):
        command_list = {}
        command_list["probability"] = Probability(command_key, self.client)
        return command_list
class Probability(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "probability", """Calculates probability""", f"{command_key} probability", ["chances"])
        self.args = Args()
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        def is_number(s):
            try:
                float(s.content)
                return True
            except ValueError:
                return False
        try:
            parse = self.parser.parse(message.content)
            if parse:
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
                    em.add_field(name="Trials", value=f"{trials}")
                    em.add_field(name="Successes", value=f"{successes}")
                    em.add_field(name="Chance", value=f"{chance}")
                    em.add_field(name="Probability", value=f"{Math.probability(trials, successes, chance)}")
                    await message.channel.send(embed=em)
        except asyncio.TimeoutError:
            await message.channel.send(embed=EmbedTemplate(title="Probability", description="Timed out"))