# TODO:
# Stage dropit/sanity cost
#   resurssi planner
#   gacha simulaattori
import random
import time
from typing import Any, Union
class ResourcePlanner():
    def __init__(self) -> None:
        self.random = random.Random(time.time())
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