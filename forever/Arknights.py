# TODO:
# Stage dropit/sanity cost
#   resurssi planner
#   gacha simulaattori
import random
import json
import time
from typing import Any, Union
class ResourcePlanner():
    def __init__(self) -> None:
        self.random = random.Random(time.time())
class PenguinStats():
    def __init__(self, database) -> None:
        self.session = None
        self.database = database
        self.url = "https://penguin-stats.io/PenguinStats/api/v2/result/matrix?server=US"
    async def get_data(self,):
        if self.session:
            async with self.session.get(self.url) as resp:
                if resp.status == 200:
                    data = json.loads(await resp.text())
                    return data
                else:
                    return None
        return None
    async def parse(self,):
        data = await self.get_data()
        if data:
            data = data["matrix"]
            for i in data:
                stageid = i["stageId"]
                itemid = i["itemId"]
                quantity = i["quantity"]
                times = i["times"]

                stage = self.database.runtime['arknights']['stages'].get(stageid)
                item = self.database.runtime['arknights']['items'].get(itemid)
                if stage and item:
                    if stage.drops:
                        for x in range(len(stage.drops)):
                            if item == stage.drops[x]["item"]:
                                stage.drops[x]["quantity"] = quantity
                                stage.drops[x]["times"] = times
                                break
                    if item.stage_drop_list:
                        for x in range(len(item.stage_drop_list)):
                            if stage == item.stage_drop_list[x]["stage"]:
                                item.stage_drop_list[x]["quantity"] = quantity
                                item.stage_drop_list[x]["times"] = times
                                break

class Stage():
    def __init__(self, id : str, code : str, name : str, description : str, sanity_cost : int, drops : list[dict[str, Any]]) -> None:
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.sanity_cost = sanity_cost
        self.drops = drops
class Item():
    def __init__(self, id : str, name : str, description : str, rarity : int, icon_id : str, usage : str, stage_drop_list : list[dict[str, Any]]=None, formula : Any=None) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.rarity = rarity
        self.icon_id = icon_id
        self.usage = usage
        self.stage_drop_list = stage_drop_list
        self.formula = formula
        self._stage_drop_list_str = None
    def set_formula(self, formula : Any) -> None:
        self.formula = formula
    def set_stage_drop_list(self, stage_drop_list : list[dict[str, Any]]):
        self.stage_drop_list = stage_drop_list
class Formula():
    def __init__(self, id : str, item : Any, count : int, costs : list[dict[str, Union[Any, int]]], room : str) -> None:
        self.id = id
        self.item = item
        self.count = count
        self.costs = costs
        self.room = room
class BannerSimulator():
    # 6 stars x float
    # 5 stars x float
    #other:
    #6 star 2%
    #5 star 8%
    #4 star 50%
    #3 star 40%

    #after 50 rolls if no 6 star, the roll is increased by 2% per roll if no 6 star, resets
    def __init__(self) -> None:
        self.six_star = {"weight" : 0.02, "without" : 0}
        self.droptable = {
            0.08 : [],
            0.5 : [],
            0.4 : []
        }
    def roll(self, n=1):
        pass