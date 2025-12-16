import numpy as np
from numpy.linalg import norm, pinv
from matplotlib import pyplot as plt

class RBF:
    def __init__(self, indim, numCenters, outdim):
        self.indim = indim
        self.outdim = outdim
        self.numCenters = numCenters
        self.centers = [np.random.uniform(-1, 1, indim) for _ in range(numCenters)]
        self.beta = 8
        self.W = np.random.randn(self.numCenters, self.outdim)
    
    def _basisfunc(self, c, d):
        assert len(d) == self.indim
        return np.exp(-self.beta * norm(c - d)**2)
    
    def _calcAct(self, X):
        G = np.zeros((X.shape[0], self.numCenters))
        for ci, c in enumerate(self.centers):
            for xi, x in enumerate(X):
                G[xi, ci] = self._basisfunc(c, x)
        return G
    
    def train(self, X, Y):
        rnd_idx = np.random.permutation(X.shape[0])[:self.numCenters]
        self.centers = [X[i, :] for i in rnd_idx]
        print("centers:", self.centers)
        
        G = self._calcAct(X)
        print("Activation Matrix G:\n", G)
        
        self.W = np.dot(pinv(G), Y)
    
    def test(self, X):
        G = self._calcAct(X)
        Y = np.dot(G, self.W)
        return Y

# 1D Example
if __name__ == '__main__':
    n = 100
    x = np.linspace(-1, 1, n).reshape(n, 1)
    y = np.sin(3 * (x + 0.5) ** 3 - 1)
    
    rbf = RBF(1, 10, 1)
    rbf.train(x, y)
    z = rbf.test(x)
    
    # Plot original data and RBF output
    plt.figure(figsize=(12, 8))
    plt.plot(x, y, 'k-', label='Original Function')
    plt.plot(x, z, 'r-', linewidth=2, label='RBF Output')
    
    # Plot centers
    center_x = [c[0] for c in rbf.centers]
    plt.plot(center_x, np.zeros(rbf.numCenters), 'gs', label='Centers')
    
    # Plot RBFs
    for c in rbf.centers:
        cx = np.arange(c[0] - 0.7, c[0] + 0.7, 0.01)
        cy = [rbf._basisfunc(np.array([c[0]]), np.array([cx_])) for cx_ in cx]
        plt.plot(cx, cy, '-', color='gray', linewidth=0.3)
    
    plt.title("RBF Network Function Approximation")
    plt.legend()
    plt.xlim(-1.2, 1.2)
    plt.grid(True)
    plt.show()
