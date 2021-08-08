from typing import Any

import discord
from models.EmbedTemplate import EmbedTemplate
from forever.ProbabilitySim import BoolWeightedPool
import config
import datetime
import random
class Doll:
    def __init__(self, doll_id : int, name : str, doll_type : str, rarity : str, formation_bonus : str, formation_tiles : str, skill : str, aliases : list[str], production_timer : int=None):
        self.doll_id = doll_id
        self.name = name
        self.doll_type = doll_type
        self.rarity = rarity
        self.formation_bonus = formation_bonus
        self.formation_tiles = formation_tiles
        self.skill = skill
        self.aliases = aliases
        self.production_timer = production_timer
    def get_image_path(self,) -> str:
        file_name = self.name.replace(" ", "_").replace("/","")
        return f"{config.asset_path}/images/gfl/dolls/128x167_{file_name}.png"
    def get_embed(self,) -> discord.Embed:
        em = EmbedTemplate(title=self.name)
        if self.production_timer:
            em.add_field(name="Production Time", value=f"{datetime.timedelta(seconds=self.production_timer)}", inline=False)
        
        em.add_field(name="Skill", value=self.skill if self.skill else "N/A")
        if self.formation_bonus and self.formation_tiles:
            formation_tiles = self.formation_tiles.replace("0", "⬛").replace("1", "⬜").replace("2", "🟦").replace("\\r\\n", "\r\n")
            formation_bonus = self.formation_bonus.replace("\\r\\n", "\r\n")
            em.add_field(
                name="Formation",
                value=f"{formation_tiles}\n\n{formation_bonus}",
                inline=False
            )
        return em
    def __repr__(self) -> str:
        return f'<GFL.Doll name={self.name}, id={self.doll_id}>'
class Fairy:
    def __init__(self, fairy_id : int, name : str, stats : str, skill : str, production_timer : int) -> None:
        self.fairy_id = fairy_id
        self.name = name
        self.stats = stats.split("|")
        self.skill = skill
        self.production_timer = production_timer
    def get_embed(self,) -> discord.Embed:
        em = EmbedTemplate(title=self.name)
        if self.production_timer:
            em.add_field(
                name="Production Time",
                value=f"{datetime.timedelta(seconds=self.production_timer)}",
                inline=False
            )
        if self.stats:
            em.add_field(name="Stats", value="\n".join(self.stats))
        em.add_field(name="Skill", value=self.skill if self.skill else "N/A")
        
        return em
class ProtocolAssimilationBanner():
    PRIORITIZE_WEIGHT = "PRIORITY_WEIGHT"
    MONTHLY_SVAROGS = 6
    class BannerItem():
        def __init__(self, name, amount) -> None:
            self.name = name
            self._original_amount = amount
            self._amount = amount
        def original_amount(self,) -> int:
            return self._original_amount
        def reduce_by_one(self,) -> None:
            self._amount -= 1
        def reset(self,) -> None:
            self._amount = self._original_amount
        def amount(self,) -> int:
            return self._amount
    def __init__(self, svarog_tickets_from_previous : int=0) -> None:
        self.pool = BoolWeightedPool()
        self.svarog_tickets = svarog_tickets_from_previous
        self.names = None
        self.prioritized_list = [ProtocolAssimilationBanner.PRIORITIZE_WEIGHT]
    def set_names(self, names : dict) -> None:
        self.names = names
        self.banner_counts()
    def add(self, weight : float, amount : int) -> None:
        self.pool.add(weight, amount)
    def set_prioritize(self, prioritized_list : list[str]) -> None:
        self.prioritized_list = prioritized_list + self.prioritized_list
    def load(self, data : dict[float, int]) -> None:
        for weight, amount in data.items():
            self.pool.add(weight, amount)
    def get_banner_item(self, weight : float) -> Any:
        if self.names:
            tmp = self.names.get(weight)
            if tmp:
                item = random.choice(tmp)
                while item.amount() == 0:
                    item = random.choice(tmp)
                return item
    def banner_counts(self,) -> None:
        for weight, items in self.names.items():
            total = 0
            for item in items:
                total += item.amount()
            self.add(weight, total)
    def reset(self,) -> None:
        self.pool.reset()
        for weight, items in self.names.items():
            for item in items:
                item.reset()
        self.banner_counts()
    def run(self, stop_if_ringleader : bool=True) -> tuple[int, dict[int, dict]]:
        pulls = 1
        results = {}
        slots = {
            1 : (None, None, None),
            2 : (None, None, None),
            3 : (None, None, None),
        }
        for i in range(3):
            if self.pool.has_items():
                weight, success = self.pool.get()
                slots[i+1] = (self.get_banner_item(weight), weight, success)
        chosen_index = None
        chosen_item = None
        while self.pool.has_items():
            if self.pool.pool_count() <= self.svarog_tickets:
                while self.pool.has_items():
                    weight2 = self.pool.items.pop()
                    banner_item = self.get_banner_item(weight2)
                    if banner_item.name not in results:
                        results[banner_item.name] = {}
                        results[banner_item.name]["item"] = banner_item
                        results[banner_item.name]["failures"] = 0
                        results[banner_item.name]["successes"] = 0
                        results[banner_item.name]["total"] = 0
                        results[banner_item.name]["svarogs"] = 0
                    if "svarogs" not in results[banner_item.name]:
                        results[banner_item.name]["svarogs"] = 0
                    
                    results[banner_item.name]["successes"] += 1
                    results[banner_item.name]["total"] += 1
                    results[banner_item.name]["svarogs"] += 1
                    if weight2 == 1/4 and stop_if_ringleader:
                        return pulls, results
                return pulls, results
            elif self.prioritized_list:
                banner_item_1, weight_1, success_1 = slots[1]
                banner_item_2, weight_2, success_2 = slots[2]
                banner_item_3, weight_3, success_3 = slots[3]
                slots_banner_items = [banner_item_1, banner_item_2, banner_item_3]
                slots_weights = [weight_1, weight_2, weight_3]
                if chosen_item and chosen_index:
                    weight, success = self.pool.get()
                    slots[chosen_index] = (self.get_banner_item(weight), weight, success)
                for i in self.prioritized_list:
                    index = 0
                    do_break = False
                    for x in slots_weights:
                        if x == 1/4:
                            chosen_item = slots[index+1]
                            chosen_index = index+1
                            do_break = True
                            break
                        index += 1
                    if do_break:
                        break
                    elif i == ProtocolAssimilationBanner.PRIORITIZE_WEIGHT:
                        largest = max(slots_weights)
                        index = slots_weights.index(largest)
                        chosen_item = slots[index+1]
                        chosen_index = index+1
                        break
                    else:
                        index = 0
                        for x in slots_banner_items:
                            if x.name == i:
                                chosen_item = slots[index+1]
                                chosen_index = index+1
                                break
                            index += 1
                banner_item, chosen_weight, chosen_success = chosen_item

                if banner_item.name not in results:
                    results[banner_item.name] = {}
                    results[banner_item.name]["item"] = banner_item
                    results[banner_item.name]["failures"] = 0
                    results[banner_item.name]["successes"] = 0
                    results[banner_item.name]["total"] = 0
                results[banner_item.name]["total"] += + 1
                if chosen_success:
                    results[banner_item.name]["successes"] += 1
                    banner_item.reduce_by_one()
                    if chosen_weight == 1/4 and stop_if_ringleader:
                        return pulls, results
                else:
                    results[banner_item.name]["failures"] += 1
                pulls += 1
        
        return pulls, results

class Banners():
    @staticmethod
    def hunter() -> dict[int, list[ProtocolAssimilationBanner.BannerItem]]:
        return {
        1 : [
            ProtocolAssimilationBanner.BannerItem("Vespid", 10),
            ProtocolAssimilationBanner.BannerItem("Ripper", 10),
            ProtocolAssimilationBanner.BannerItem("Guard", 10),
            ProtocolAssimilationBanner.BannerItem("Jaeger", 10),
            ProtocolAssimilationBanner.BannerItem("Striker", 10),
            ProtocolAssimilationBanner.BannerItem("Scout", 10),
            ProtocolAssimilationBanner.BannerItem("Prowler", 11),
        ],
        1/2 : [
            ProtocolAssimilationBanner.BannerItem("Manticore", 5),
            ProtocolAssimilationBanner.BannerItem("Nemeum", 5),
            ProtocolAssimilationBanner.BannerItem("Aegis", 6),
            ProtocolAssimilationBanner.BannerItem("Dragoon", 6),
            ProtocolAssimilationBanner.BannerItem("Brute", 6)
        ],
        1/4 : [
            ProtocolAssimilationBanner.BannerItem("Hunter", 1)
        ]
    }

if __name__ == "__main__":
    # tmp = {
    #     1/256 : ["Serpentine Visage", "Toxic Blowpipe"],
    #     1/30 : "Yew Log",
    #     1/10 : "Oak log",
    #     1/5 : "Flax"
    # }
    compiled = []
    names = {
        1 : {
            "Vespid" : 10,
            "Ripper" : 10,
            "Guard" : 10,
            "Jaeger" : 10,
            "Striker" : 10,
            "Scout" : 10,
            "Prowler" : 11,
        },
        1/2 : {
            "Manticore" : 5,
            "Nemeum" : 5,
            "Aegis" : 6,
            "Dragoon" : 6,
            "Brute" : 6
        },
        1/4 : {
            "Hunter" : 1
        }
    }
    dt = ProtocolAssimilationBanner(10)
    dt.set_names(names)
    dt.set_prioritize("Manticore", "Nemeum")
    total = 0
    banner_count = 1000
    for i in range(banner_count):
        dt.reset()
        pulls, results = dt.run(False)
        total += pulls
        print(f"Got after {pulls} pulls.")
    print(f"Total Pulls {total} across {banner_count} Banners\nAverage {total/banner_count}\n")