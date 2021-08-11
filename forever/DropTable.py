from forever.ProbabilitySim import ConstantPool, BoolWeightedPool
import random
#Testi tiedosto, ei käytössä ->

class DropTable():
    def __init__(self,) -> None:
        pool = ConstantPool()
        self.simulator = Simulation(pool)
    def add(self, weight, item):
        self.simulator.pool.add(weight, item)
    def load(self, data):
        for weight, item in data.items():
            if isinstance(item, list):
                for i in item:
                    self.simulator.pool.add(weight, i)
            else:
                self.simulator.pool.add(weight, item)
    def set_rolls(self, rolls):
        self.simulator.pool.rolls = rolls
    def run(self, rolls):
        self.set_rolls(rolls)
        items = self.simulator.run()
        tmp = {}
        for i in items:
            weight, item = i
            if item not in tmp:
                tmp[item] = 0
            tmp[item] += 1
        return tmp
class ProtocolAssimilationBanner():

    PRIORITIZE_WEIGHT = "PRIORITY_WEIGHT"
    MONTHLY_SVAROGS = 6
    class BannerItem():
        def __init__(self, name, amount) -> None:
            self.name = name
            self._original_amount = amount
            self._amount = amount
        def reduce_by_one(self,):
            self._amount -= 1
        def reset(self,):
            self._amount = self._original_amount
        def amount(self,):
            return self._amount
    def __init__(self, svarog_tickets_from_previous=0) -> None:
        self.pool = BoolWeightedPool()
        self.svarog_tickets = svarog_tickets_from_previous
        self.names = None
        self.prioritized_list = [ProtocolAssimilationBanner.PRIORITIZE_WEIGHT]
    def set_names(self, names):
        self.names = names
        self.banner_counts()
    def add(self, weight, amount):
        self.pool.add(weight, amount)
    def set_prioritize(self, prioritized_list):
        self.prioritized_list = prioritized_list + self.prioritized_list
    def load(self, data):
        for weight, amount in data.items():
            self.pool.add(weight, amount)
    def get_name(self, weight):
        if self.names:
            tmp = self.names.get(weight)
            if tmp:
                item = random.choice(tmp)
                while item.amount() == 0:
                    item = random.choice(tmp)
                return item
    def banner_counts(self,):
        for weight, items in self.names.items():
            total = 0
            for item in items:
                total += item.amount()
            self.add(weight, total)
    def reset(self,):
        self.pool.reset()
        for weight, items in self.names.items():
            for item in items:
                item.reset()
        self.banner_counts()
    def run(self, stop_if_ringleader=True):
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
                slots[i+1] = (self.get_name(weight), weight, success)
        chosen_index = None
        chosen_item = None
        while self.pool.has_items():
            if self.pool.pool_count() <= self.svarog_tickets:
                while self.pool.has_items():
                    weight2, success2 = self.pool.get()
                    success2 = True
                    if weight2 not in results:
                        results[weight2] = {}
                        results[weight2]["success"] = 0
                        results[weight2]["failures"] = 0
                        results[weight2]["total"] = 0
                return pulls, results
            elif self.prioritized_list:
                name_1, weight_1, success_1 = slots[1]
                name_2, weight_2, success_2 = slots[2]
                name_3, weight_3, success_3 = slots[3]
                names = [name_1, name_2, name_3]
                weights = [weight_1, weight_2, weight_3]
                if chosen_item and chosen_index:
                    weight, success = self.pool.get()
                    slots[chosen_index] = (self.get_name(weight), weight, success)
                for i in self.prioritized_list:
                    index = 0
                    do_break = False
                    for x in weights:
                        if x == 1/4:
                            chosen_item = slots[index+1]
                            chosen_index = index+1
                            do_break = True
                            break
                        index += 1
                    if do_break:
                        break
                    elif i == ProtocolAssimilationBanner.PRIORITIZE_WEIGHT:
                        largest = max(weights)
                        index = weights.index(largest)
                        chosen_item = slots[index+1]
                        chosen_index = index+1
                        break
                    else:
                        index = 0
                        for x in names:
                            if x.name == i:
                                chosen_item = slots[index+1]
                                chosen_index = index+1
                                break
                            index += 1
                chosen_name, chosen_weight, chosen_success = chosen_item
                if chosen_weight not in results:
                    results[chosen_weight] = {}
                    results[chosen_weight]["success"] = 0
                    results[chosen_weight]["failures"] = 0
                    results[chosen_weight]["total"] = 0
                results[chosen_weight]["total"] += 1
                if chosen_success:
                    results[chosen_weight]["success"] += 1
                    chosen_name.reduce_by_one()
                    if chosen_weight == 1/4 and stop_if_ringleader:
                        return pulls, results
                else:
                    results[chosen_weight]["failures"] += 1
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
    total = 0
    banner_count = 1000
    dt = ProtocolAssimilationBanner(ProtocolAssimilationBanner.MONTHLY_SVAROGS)
    dt.set_prioritize(["Manticore", "Nemeum"])
    dt.set_names(Banners.hunter())
    for i in range(banner_count):
        pulls, results = dt.run()
        total += pulls
        print(f"Got after {pulls} pulls.")
        dt.reset()
    print(f"Total Pulls {total} across {banner_count} Banners\nAverage {total/banner_count}\n")