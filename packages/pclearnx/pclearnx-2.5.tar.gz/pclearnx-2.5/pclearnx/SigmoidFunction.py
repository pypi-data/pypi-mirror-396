import math
n = int(input("Enter number of elements: "))
print("Enter the inputs:")
inputs = []
for i in range(n):
    ele = float(input())
    inputs.append(ele)
print("Inputs:", inputs)

print("Enter the weights:")
weights = []
for i in range(n):
    ele = float(input())
    weights.append(ele)
print("Weights:", weights)

b = float(input("Enter bias value: "))

print("The net input can be calculated as Yin = b + x1w1 + x2w2:")
Yin = []
for i in range(n):
    Yin.append(inputs[i] * weights[i])

net_input = round(sum(Yin) + b, 3)
print("Net input (Yin):", net_input)

binary_output = 1 / (1 + math.exp(-net_input))
print("Binary Sigmoidal Output:", round(binary_output, 3))

bipolar_output = math.tanh(net_input)
print("Bipolar Sigmoidal Output:", round(bipolar_output, 3))
