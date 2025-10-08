import numpy as np
import matplotlib.pyplot as plt


def moveCA(p, q, r, v):
    ind = 4 * p + 2 * q + r
    return v[ind]


def checkBinary(vec):
    for i in vec:
        if i not in [0, 1]:
            raise ValueError("Вектор должен быть двоичным")


ca = input("Введите правило: ")
if len(ca) != 8:
    raise ValueError("Длина вектора КА должна быть равна 8")
v = [int(j) for j in ca]
checkBinary(v)

N = int(input("Введите N: "))

input_vec = input("Введите начальное положение x_0: ")
if len(input_vec) != N:
    raise ValueError("Длина вектора x_0 != N")
arr = [int(j) for j in input_vec]
checkBinary(arr)

gens = int(input("Введите число шагов: "))
history = []

for _ in range(gens):
    n = len(arr)
    new_arr = [0] * n
    for i in range(n):
        p = arr[(i - 1) % n]
        q = arr[i]
        r = arr[(i + 1) % n]
        new_arr[i] = moveCA(p, q, r, v)
    history.append(arr)
    arr = new_arr

print("Шаг\t | x_i" + " " * (N - 3) + " |")
for i in range(len(history)):
    print(str(i) + "\t |", end=" ")
    for j in history[i]:
        print(j, end="")
    print(" |")


fig, ax = plt.subplots()
img = ax.matshow(np.array(history), cmap="binary", aspect="equal")
ax.set_title("Одномерный клеточный автомат")
ax.set_xlabel("Индекс клетки")
ax.set_ylabel("Шаг")
ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
ax.set_yticks(np.arange(-0.5, gens, 1), minor=True)
ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5)
plt.show()
