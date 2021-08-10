import asyncio
from typing import Any
import discord
import re
import datetime

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from models.Server import Server
from forever.Database import DB_API
from forever.GFL import Doll, ProtocolAssimilationBanner, Banners
from forever.Utilities import Args
#fairylle komennot, dolleille jonkinlainen haku

class GFLCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.client = client
        self.database = database
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetch_commands(self, command_key):
        command_list = {}
        command_list["production"] = ProductionDolls(command_key, self.client, self.database)
        command_list["doll"] = DollInfo(command_key, self.client, self.database)
        command_list["sfsim"] = SFCapture(command_key)
        return command_list
class ProductionDolls(Command):
    def __init__(self, command_key, client, database):
        self.client = client
        self.database = database
        super().__init__(command_key, "production", """Production Dolls""", f"{command_key} production", ["production","prod", "pr"])
        self.args = Args()
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message : discord.Message, server : Server):
        parsed = self.args.parse(message.content)
        if parsed:
            tmp = list(self.database.runtime["gfl"]["dolls"]["names"].values())
            tmp = [x for x in tmp if x.production_timer]
            tmp_str = []
            for doll in sorted(tmp, key=lambda x: x.production_timer):
                tmp_str.append(f"{datetime.timedelta(seconds=doll.production_timer)} {doll.name} {doll.doll_type}")
            lists = [tmp_str[i:i+30] for i in range(0, len(tmp_str), 30)]
            em = EmbedTemplate(title="Production Dolls")
            for i in lists:
                em.add_field(name="PRODUCTION", value="\n".join(i), inline=True)
            await message.channel.send(embed=em)
class DollInfo(Command):
    def __init__(self, command_key : str, client : discord.Client, database : DB_API):
        self.client = client
        self.database = database
        super().__init__(command_key, "doll", """Info of dolls""", f"{command_key} doll", ["d", "tdoll"])
        self.args = Args(doll=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    def find_doll(self, parse : str) -> Doll:
        if parse['doll'].lower() in self.database.runtime["gfl"]["dolls"]["names"]:
            return self.database.runtime["gfl"]["dolls"]["names"].get(parse['doll'].lower())
        elif parse['doll'].lower() in self.database.runtime["gfl"]["dolls"]["aliases"]:
            return self.database.runtime["gfl"]["dolls"]["aliases"].get(parse['doll'].lower())
        else:
            return None
    async def run(self, message : discord.Message, server : Server) -> None:
        parse = self.args.parse(message.content)
        if parse:
            doll = self.find_doll(parse)
            if doll:
                em = doll.get_embed()
                image = discord.File(doll.get_image_path(), filename="doll.png")
                em.set_image(url="attachment://doll.png")
                await message.channel.send(file=image, embed=em)
            else:
                em = EmbedTemplate(title="Not found", description="Doll wasn't found in the database, if you think this is an error, contact bot owner.")
                await message.channel.send(embed=em)
class SFCapture(Command):
    def __init__(self, command_key,):
        super().__init__(command_key, "sfsim", """SF Capture sim""", f"{command_key} sfsim", ["sfcap"])
        self.args = Args(banner=Args.STRING_ARG, amount=Args.OPTIONAL_INT_ARG)
        self.args.set_pattern(command_key, self.aliases)
    def combine_results(self, data : list[dict[str, dict[str, Any]]]) -> tuple[dict[str, dict[str, Any]], int]:
        combined_results = {}
        total_svarogs = 0
        for results in data:
            for banner_unit_name, banner_unit_data in results.items():
                if banner_unit_name not in combined_results:
                    combined_results[banner_unit_name] = {}
                    combined_results[banner_unit_name]["failures"] = 0
                    combined_results[banner_unit_name]["successes"] = 0
                    combined_results[banner_unit_name]["total"] = 0
                    combined_results[banner_unit_name]["item"] = banner_unit_data["item"]
                combined_results[banner_unit_name]["failures"] += banner_unit_data["failures"]
                combined_results[banner_unit_name]["successes"] += banner_unit_data["successes"]
                combined_results[banner_unit_name]["total"] += banner_unit_data["total"]
                if 'svarogs' in banner_unit_data:
                    if 'svarogs' not in combined_results[banner_unit_name]:
                        combined_results[banner_unit_name]["svarogs"] = 0
                    combined_results[banner_unit_name]["svarogs"] += banner_unit_data["svarogs"]
                    total_svarogs += banner_unit_data["svarogs"]
        return combined_results, total_svarogs
    async def run(self, message : discord.Message, server : Server) -> None:
        parse = self.args.parse(message.content)
        if parse:
            amount = int(parse['amount']) if parse['amount'] else 1
            banner = parse['banner'] 
            items = None
            if banner == "hunter":
                items = Banners.hunter()
            if amount > 500:
                amount = 500
            if items:
                sim = ProtocolAssimilationBanner(ProtocolAssimilationBanner.MONTHLY_SVAROGS)
                sim.set_names(items)
                sim.set_prioritize(["Manticore", "Nemeum", ProtocolAssimilationBanner.PRIORITIZE_WEIGHT])
                total_pulls = 0
                total_results = []
                for i in range(amount):
                    pulls, results = sim.run()
                    total_pulls += pulls
                    total_results.append(results)
                    sim.reset()
                combined_results, used_svarogs = self.combine_results(total_results)
                total_svarogs = sim.svarog_tickets * amount

                em = EmbedTemplate(title="Sim", description=f"Across {amount} banners, you got:\nTotal pulls: {total_pulls}\nTotal SVAROG tickets used: {used_svarogs}/{total_svarogs}")
                for banner_item_name, banner_item_data in combined_results.items():
                    em.add_field(name=banner_item_name, value=f"""
                    {f"Svarogs: {banner_item_data['svarogs']}" if 'svarogs' in banner_item_data else ""}
                    {f"Failures: {banner_item_data['failures']}" if banner_item_data['failures'] > 0 else ""}
                    Successes: {banner_item_data['successes']}
                    Total: {banner_item_data['total']}
                    Got {banner_item_data['successes']}/{banner_item_data['item']._original_amount*amount}
                    """)
                await message.channel.send(embed=em)




