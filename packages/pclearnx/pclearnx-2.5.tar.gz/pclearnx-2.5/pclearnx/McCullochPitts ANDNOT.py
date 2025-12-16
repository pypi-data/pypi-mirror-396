num_ip = int(input("Enter the number of inputs: "))
w1 = 1
w2 = 1
print(f"For the {num_ip} inputs calculate the net input using yin = x1w1 + x2w2")
x1 = []
x2 = []

for j in range(num_ip):
    ele1 = int(input("x1 = "))
    ele2 = int(input("x2 = "))
    x1.append(ele1)
    x2.append(ele2)

print("x1 =", x1)
print("x2 =", x2)

n = [x * w1 for x in x1]
m = [x * w2 for x in x2]

Yin = [n[i] + m[i] for i in range(num_ip)]
print("Yin =", Yin)

Yin = [n[i] - m[i] for i in range(num_ip)]
print("After assuming one weight as excitatory and the other as inhibitory Yin =", Yin)

Y = []
for i in range(num_ip):
    if Yin[i] >= 1:
        Y.append(1)
    else:
        Y.append(0)

print("Y =", Y)
