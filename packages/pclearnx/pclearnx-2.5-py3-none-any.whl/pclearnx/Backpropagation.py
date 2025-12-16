import numpy as np
import math

np.set_printoptions(precision=2)

v1 = np.array([0.6, 0.3])
v2 = np.array([-0.1, 0.4])
w = np.array([-0.2, 0.4, 0.1])
b1, b2 = 0.3, 0.5
x1, x2 = 0, 1
lr = 0.25

z1_in = b1 + x1*v1[0] + x2*v2[0]
z2_in = b2 + x1*v1[1] + x2*v2[1]
print("z1_in =", round(z1_in, 4))
print("z2_in =", round(z2_in, 4))

z1 = 1/(1+math.exp(-z1_in))
z2 = 1/(1+math.exp(-z2_in))
print("z1 =", round(z1,4))
print("z2 =", round(z2,4))

y_in = w[0] + z1*w[1] + z2*w[2]
print("y_in =", y_in)

y = 1/(1+math.exp(-y_in))
print("y =", y)

fy = y*(1-y)
dk = (1-y)*fy
print("dk =", dk)

dw0 = lr*dk
dw1 = lr*dk*z1
dw2 = lr*dk*z2

d1 = dk*w[1]*z1*(1-z1)
d2 = dk*w[2]*z2*(1-z2)
print("d1 =", d1)
print("d2 =", d2)

dv11 = lr*d1*x1
dv21 = lr*d1*x2
db1 = lr*d1

dv12 = lr*d2*x1
dv22 = lr*d2*x2
db2 = lr*d2

v1 += np.array([dv11, dv12])
v2 += np.array([dv21, dv22])

w[0] += dw0
w[1] += dw1
w[2] += dw2

b1 += db1
b2 += db2

print("v1 =", v1)
print("v2 =", v2)
print("w =", w)
print("b1 =", b1, "b2 =", b2)
