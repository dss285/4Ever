from forever.ProbabilitySim import ConstantPool, Simulation
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
if __name__ == "__main__":
    tmp = {
        1/256 : ["Serpentine Visage", "Toxic Blowpipe"],
        1/30 : "Yew Log",
        1/10 : "Oak log",
        1/5 : "Flax"
    }
    dt = DropTable()
    dt.load(tmp)
    print(dt.run(30000))
