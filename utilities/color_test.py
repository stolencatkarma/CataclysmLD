# outputs Color codes to the console for reference.
print()
print(" Printing FOREGROUND COLORS")
pre_color = "\u001b[38;5;"
reset = "\u001b[0m"
for i in range(0, 16):
    for j in range(1, 17):
        next = str(i * 16 + j)
        print(str(pre_color + next + "m" + next + reset), end = " ")
    print()

print()
print(" Printing BACKGROUND COLORS")
pre_color = "\u001b[48;5;"
for i in range(0, 16):
    for j in range(0, 16):
        next = i * 16 + j
        print(str("\u001b[38;5;0m" + pre_color + str(next) + "m" + str(next) + reset).rjust(5, " "), end = " ")
    print()
