import numpy as np

# First 
x1 = np.array([1, 1, 1, -1, 1, -1, 1, 1, 1])

# Second
x2 = np.array([1, 1, 1, 1, -1, 1, 1, 1, 1])

b = 0

y = np.array([1, -1])
wtold = np.zeros((9,))
wtnew = np.zeros((9,))
wtnew = wtnew.astype(int)
wtold = wtold.astype(int)
bais = 0

print("First input with target = 1")
for i in range(0, 9):
    wtold[i] = wtold[i] + x1[i] * y[0]

wtnew = wtold
b = b + y[0]
print("new wt =", wtnew)
print("Bias value", b)
print("\nSecond input with target = -1")
for i in range(0, 9):
    wtnew[i] = wtold[i] + x2[i] * y[1]
b = b + y[1]
print("new wt =", wtnew)
print("Bias value", b)
