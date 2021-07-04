import math
from re import T
import time
import threading
import multiprocessing
from typing import Optional
import random
"""
    Probability Simulator, provides different kind of "pools" to get items from

    AbstractPool - AbstractClass just to make sure all pools implement methods
    All pools return tuple.
    Has clone ability to make new of the same object for in use of Simulator Class




"""
class AbstractPool():
    def __init__(self) -> None:
        self.items = None
    def has_items(self,):
        raise NotImplementedError()
    def add(self,):
        raise NotImplementedError()
    def get(self,):
        raise NotImplementedError()
    def clone(self,):
        raise NotImplementedError()
class ConstantPool(AbstractPool):
    "Pool where there is only limited polls, and roll whether rolled item is success"
    def __init__(self, rolls=3000) -> None:
        self.items = {}
        self.random = random.Random(time.time())
        self.rolls = rolls
    def has_items(self,) -> bool:
        return 0<self.rolls
    def add(self, weight, item) -> None:
        if weight not in self.items:
            self.items[weight] = []
        self.items[weight].append(item)
    def weights(self,) -> dict:
        return sorted(self.items.keys(), reverse=True)
    def get(self,) -> tuple:
        tmp = self.random.uniform(0, 1)
        weight = False
        for i in self.weights():
            if tmp < i:
                weight = i
        self.rolls -= 1
        if weight:
            return ((weight, self.random.choice(self.items[weight])), True)
        else:
            return ((None, None), None)
    def clone(self):
        tmp = ConstantPool(self.rolls)
        tmp.items = self.items
        return tmp
class WeightedPool(AbstractPool):
    """ 
    WeightedPool - Rolls number whether you get item or not, depending what weights you put items, if for example items are:
    0.5 : 3
    0.25 : 3
    0.1 : 3
    You roll 0.6, you get None
    You roll 0.4, you get 0.5, after that 0.5 items decrease by one, and if it reaches zero, it's deleted from the pool
    You roll 0.01 you get 0.1, same behavior as in 0.5
    You roll 0.12 you get 0.25, same behavior as in 0.5
    """
    def __init__(self,) -> None:
        self._items = None
        self.items = {}
        self.random = random.Random(time.time())
    def has_items(self,) -> bool:
        return True if self.items else False
    def add(self, weight, amount) -> None:
        if weight not in self.items:
            self.items[weight] = 0
        self.items[weight] += amount
    def weights(self,) -> dict:
        return sorted(self.items.keys(), reverse=True)
    def get(self,) -> tuple:
        if self.__items is None:
            self.__items = dict(self.items)
        tmp = self.random.uniform(0, 1)
        weight = False
        for i in self.weights():
            if tmp < i:
                if self.items[i] != 0:
                    weight = i
                else:
                    del self.items[i]
        if weight:
            if self.items[weight] != 0:
                self.items[weight] -= 1
            else:
                del self.items[weight]
            return (weight, True)
        else:
            return (None, None)
    def clone(self,) -> AbstractPool:
        if self._items is None:
            self._items = dict(self.items)
        tmp = WeightedPool()
        tmp.items = dict(self._items)
        return tmp
class BoolWeightedPool(AbstractPool):
    """ 
    BoolWeightedPool - Has guaranteed chance to get one item, but can result in failure if weight in the item is under the rolled number, if for example items are:
    [0.5, 0.25, 0.1]
    You request it, you get whether particular weight was successful or not.
    It gets 0.25 and you roll 0.12, that is success so it returns tuple of (0.25, True). Item is also now removed from the pool
    It gets 0.5 and you roll 0.6, that is failure so it returns tuple of (0.5, False). Same behavior as above.
    """
    def __init__(self) -> None:
        self._items = None
        self._weights = set()
        self.items = []
        self.random = random.Random(time.time())
    def has_items(self,) -> bool:
        return True if self.items else False

    def add(self, weight, amount) -> None:
        self._weights.add(weight)
        for i in range(amount):
            self.items.append(weight)
    def weights(self,) -> dict:
        return sorted(list(self._weights), reverse=True)
    def get(self,) -> tuple:
        if self._items is None:
            self._items = list(self.items)
        if self.items:
            self.random.shuffle(self.items)
            weight = self.items.pop()
            rng = self.random.uniform(0, 1)
            success = False
            if rng < weight:
                success = True
            if not success:
                self.add(weight, 1)
            return (weight, success)
        return (None, None)
    def clone(self,) -> AbstractPool:
        if self._items is None:
            self._items = list(self.items)
        tmp = BoolWeightedPool()
        tmp._weights = set(self._weights)
        tmp.items = list(self._items)
        return tmp
class Simulation():
    """
    Uses different pools to get successes, failures etc
    """
    def __init__(self, pool: AbstractPool) -> None:
        self.pool = pool
    def _set_pool(self, pool: AbstractPool) -> None:
        self.pool = pool
    def run(self,) -> tuple:
        is_constant_pool = isinstance(self.pool, ConstantPool)
        compilation = {}
        items = []
        while self.pool.has_items():
            weight, success = self.pool.get()
            if is_constant_pool:
                weight, item = weight
                if weight is not None:
                    items.append((weight, item))
                continue
            if weight is not None:
                if weight not in compilation:
                    compilation[weight] = {"successes" : 0, "failures" : 0, "total" : 0}
                if success:
                    compilation[weight]["successes"] += 1
                else:
                    compilation[weight]["failures"] += 1
                compilation[weight]["total"] += 1
        if is_constant_pool:
            return items
            
        combined_success = 0
        combined_failures = 0
        combined_total = 0
        for weight, data in compilation.items():
            if weight != 1:
                combined_success += data["successes"]
                combined_failures += data["failures"]
                combined_total += data["total"]
        return (combined_success, combined_failures, combined_total, compilation)
class BulkSimulation(Simulation):
    """
    Same as Simulation, but this runs it in loops
    """
    def __init__(self, pool: AbstractPool) -> None:
        super().__init__(pool)
        self.clone = pool.clone()
    def run(self, amount : int, data=None) -> None:
        combined_success = 0
        combined_failures = 0
        combined_total = 0
        combined_data = {}
        items = []
        is_constant_pool = isinstance(self.clone, ConstantPool)
        for i in range(amount):
            if is_constant_pool:
                items.extend(super().run())
                tmp = self.clone.clone()
                super()._set_pool(tmp)
            else:
                success, failures, total, _data = super().run()
                combined_success += success
                combined_failures += failures
                combined_total += total
                if not combined_data:
                    combined_data = _data
                else:
                    for weight, iter_data in _data.items():
                        combined_data[weight]["successes"] += iter_data["successes"]
                        combined_data[weight]["failures"] += iter_data["failures"]
                        combined_data[weight]["total"] += iter_data["total"]
                tmp = self.clone.clone()
                super()._set_pool(tmp)
        if is_constant_pool:
            if data:
                data.extend(items)
            print(len(items))
            return items
        for weight, iter_data in combined_data.items():
            if data:
                data[3][weight]["successes"] += iter_data["successes"]
                data[3][weight]["failures"] += iter_data["failures"]
                data[3][weight]["total"] += iter_data["total"]
  
        if data:
            data[0] += combined_success
            data[1] += combined_failures
            data[2] += combined_total
            print(data[0])
        print(f"\nTotal: {combined_total}")
        print(f"Success: {combined_success}", f"Failures: {combined_failures}")
        print(f"Rate: {(combined_success/combined_total)*100}%")
        return (combined_success, combined_failures, combined_total, combined_data)
class ThreadedBulkSimulation():
    """
        Same as BulkSimulation, but uses multiprocessing to reeally pump up some speed into it, much faster on higher counts
        Probably wont use it in any bot command, as its super heavy too
    """
    def __init__(self, pool: AbstractPool) -> None:
        self.pool = pool.clone()
        self.simulators = set()
        self.per_thread = 3000
        self.processes = []
        self.is_constant_pool = isinstance(self.pool, ConstantPool)
    def run(self, amount : int):
        if amount < self.per_thread:
            bulksim = BulkSimulation(self.pool.clone())
            bulksim.run(amount)
        else:
            manager = multiprocessing.Manager()
            data = manager.list()
            if not self.is_constant_pool:
                data.append(0)
                data.append(0)
                data.append(0)
                data.append(manager.dict())
                for i in self.pool.weights():
                    data[3][i] = {
                        "failures" : 0,
                        "successes" : 0,
                        "total" : 0
                    }
            thread_count = amount//self.per_thread
            for i in range(thread_count):
                tmp = self.pool.clone()
                bulksim = BulkSimulation(tmp)
                self.simulators.add(bulksim)
                tmp = multiprocessing.Process(target=bulksim.run, args=(self.per_thread, data,))
                self.processes.append(tmp)
                tmp.start()
            if 0 < amount%self.per_thread:
                bulksim = BulkSimulation(self.pool.clone())
                bulksim.run(amount%self.per_thread, data)
            for i in self.processes:
                i.join()
            success = data[0]
            failures = data[1]
            total = data[2]
            specific = data[3]
            # for weight, it_data in specific.items():
            #     print(f"Weight: {weight}", f"Total: {it_data['total']}")
            #     print(f"Success: {it_data['successes']}", f"Failures: {it_data['failures']}")
            #     print(f"Rate: {(it_data['successes']/it_data['total'])*100}%\n\n")
            print(f"\nTotal: {total}")
            print(f"Success: {success}", f"Failures: {failures}")
            print(f"Rate: {(success/total)*100}%")
    
if __name__ == '__main__':
    limited = ConstantPool(3000000)
    limited.add(1/256, "Toxic")
    limited.add(1/256, "Some other thing")
    limited.add(1/30, "Yew")


    # sim = ThreadedBulkSimulation(limited)
    # start = time.time()
    # sim.run(5)
    # end = time.time()-start
    # print(f"ThreadedBulk: {end}s")

    sim2 = BulkSimulation(limited)
    start = time.time()
    sim2.run(2)
    end = time.time()-start
    print(f"Bulk: {end}s")