import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class City:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def distance(self, c):
        return np.sqrt((self.x - c.x) ** 2 + (self.y - c.y) ** 2)
    def __repr__(self):
        return f"({self.x},{self.y})"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.dist = 0
        self.fit = 0
    def distance(self):
        if self.dist == 0:
            self.dist = sum(self.route[i].distance(self.route[(i+1)%len(self.route)])
                            for i in range(len(self.route)))
        return self.dist
    def value(self):
        if self.fit == 0:
            self.fit = 1 / float(self.distance())
        return self.fit

def create_route(cities):
    return random.sample(cities, len(cities))

def initial_population(n, cities):
    return [create_route(cities) for _ in range(n)]

def rank_routes(pop):
    vals = {i: Fitness(r).value() for i, r in enumerate(pop)}
    return sorted(vals.items(), key=lambda x: x[1], reverse=True)

def select(ranked, elite):
    sel = [i for i, _ in ranked[:elite]]
    df = pd.DataFrame(ranked, columns=["idx", "fit"])
    df["cum"] = df["fit"].cumsum()
    df["perc"] = 100 * df["cum"] / df["fit"].sum()
    for _ in range(len(ranked) - elite):
        p = 100 * random.random()
        for j in range(len(ranked)):
            if p <= df.iat[j, 3]:
                sel.append(ranked[j][0])
                break
    return sel

def breed(a, b):
    s, e = sorted([int(random.random()*len(a)), int(random.random()*len(a))])
    c1 = a[s:e]
    c2 = [x for x in b if x not in c1]
    return c1 + c2

def breed_pop(pool, elite):
    children = pool[:elite]
    sp = random.sample(pool, len(pool))
    children.extend(breed(sp[i], sp[-i-1]) for i in range(len(pool) - elite))
    return children

def mutate(r, rate):
    for i in range(len(r)):
        if random.random() < rate:
            j = int(random.random()*len(r))
            r[i], r[j] = r[j], r[i]
    return r

def mutate_pop(pop, rate):
    return [mutate(r, rate) for r in pop]

def next_gen(pop, elite, rate):
    ranked = rank_routes(pop)
    sel = select(ranked, elite)
    pool = [pop[i] for i in sel]
    children = breed_pop(pool, elite)
    return mutate_pop(children, rate)

def ga_plot(cities, pop_size, elite, rate, gens):
    pop = initial_population(pop_size, cities)
    progress = [1 / rank_routes(pop)[0][1]]
    for _ in range(gens):
        pop = next_gen(pop, elite, rate)
        progress.append(1 / rank_routes(pop)[0][1])
    plt.plot(progress)
    plt.xlabel("Generation")
    plt.ylabel("Distance")
    plt.grid(True)
    plt.show()

def main():
    cities = [City(int(random.random()*200), int(random.random()*200)) for _ in range(25)]
    ga_plot(cities, pop_size=100, elite=20, rate=0.01, gens=500)

if __name__ == "__main__":
    main()
