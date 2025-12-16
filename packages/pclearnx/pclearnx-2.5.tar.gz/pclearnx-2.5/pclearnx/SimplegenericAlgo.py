import random
import string

T = "Hello World"
N = 100
G = string.ascii_letters + string.digits + string.punctuation + " "

class Ind:
    def __init__(self, ch):
        self.ch = ch
        self.f = self.fit()

    def fit(self):
        return sum(1 for a, b in zip(self.ch, T) if a != b)

    @classmethod
    def rnd(cls):
        return cls([random.choice(G) for _ in range(len(T))])

    def cross(self, p):
        c = []
        for a, b in zip(self.ch, p.ch):
            r = random.random()
            if r < 0.45:
                c.append(a)
            elif r < 0.90:
                c.append(b)
            else:
                c.append(random.choice(G))
        return Ind(c)

    def __str__(self):
        return "".join(self.ch)


def ga():
    pop = [Ind.rnd() for _ in range(N)]
    gen = 0
    hist = []

    while True:
        pop.sort(key=lambda x: x.f)
        best = pop[0]
        hist.append((gen, str(best), best.f))

        if best.f == 0:
            print("Solved:", str(best), "Gen:", gen)
            break

        new = []
        e = N // 10
        new.extend(pop[:e])
        pool = pop[:N // 2]

        while len(new) < N:
            p1 = random.choice(pool)
            p2 = random.choice(pool)
            new.append(p1.cross(p2))

        pop = new
        gen += 1

    print("\nFirst 10:")
    for h in hist[:10]:
        print(f"Gen {h[0]} | {h[1]} | f={h[2]}")

    if len(hist) > 20:
        print("\nLast 10:")
        for h in hist[-10:]:
            print(f"Gen {h[0]} | {h[1]} | f={h[2]}")
    print("\nTotal Gens:", gen)


if __name__ == "__main__":
    ga()
