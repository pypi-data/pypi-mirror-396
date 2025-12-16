import numpy as np

class ART1:
    def __init__(self, d, k=10, ρ=0.75, α=0.001):
        self.d, self.k, self.ρ, self.α = d, k, ρ, α
        self.w = np.zeros((k, d), int)
        self.used = np.zeros(k, bool)

    def c(self, x):
        inter = np.sum(x & self.w, 1)
        size = np.sum(self.w, 1)
        return inter / (self.α + size)

    def m(self, x, p):
        inter = np.sum(x & p)
        return inter / np.sum(x) >= self.ρ

    def train(self, X, ep=5):
        for _ in range(ep):
            for x in X:
                x = x.astype(int)
                if np.sum(x) == 0: 
                    continue
                tried = np.zeros(self.k, bool)
                while True:
                    ch = self.c(x)
                    ch[tried] = -np.inf
                    j = np.argmax(ch)
                    if ch[j] == -np.inf:
                        break
                    if not self.used[j]:
                        self.w[j] = x
                        self.used[j] = True
                        break
                    if self.m(x, self.w[j]):
                        self.w[j] &= x
                        break
                    tried[j] = True

    def predict(self, X):
        out = []
        for x in X:
            x = x.astype(int)
            ch = self.c(x)
            ch[~self.used] = -np.inf
            out.append(None if np.all(ch == -np.inf) else np.argmax(ch))
        return out

    def protos(self):
        return self.w[self.used]


# Example
X = np.array([
    [1,1,1,0,0,0],[1,1,0,0,0,0],[1,0,1,0,0,0],
    [0,0,0,1,1,1],[0,0,0,1,1,0],[0,0,0,0,1,1],
    [1,1,0,1,0,0],[0,1,1,0,0,0],[0,0,1,1,1,0],[1,0,0,0,0,0]
])

net = ART1(d=X.shape[1], k=6, ρ=0.75)
net.train(X, ep=5)

print("Prototypes:")
for i, p in enumerate(net.protos()):
    print(f"category {i}: {p}")

print("\nAssignments:")
pred = net.predict(X)
for i, a in enumerate(pred):
    print(f"Input {i} -> category {a}")
