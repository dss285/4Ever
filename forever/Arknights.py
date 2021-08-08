# TODO:
#   resurssi planner
#   gacha simulaattori
import random
import time
class ResourcePlanner():
    def __init__(self) -> None:
        self.random = random.Random(time.time())
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