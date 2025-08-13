import turtle
import random
import math

t = turtle.Turtle()
t.speed(0)
logs = []

frame = {
    "left": -250,
    "right": 250,
    "top": 250,
    "bottom": -250
}

# Малюємо рамку
t.penup()
t.goto(frame["left"], frame["bottom"])
t.pendown()
t.goto(frame["left"], frame["top"])
t.goto(frame["right"], frame["top"])
t.goto(frame["right"], frame["bottom"])
t.goto(frame["left"], frame["bottom"])

# Стартова позиція
def teleport_to_random():
    """Телепортує в точку, яка не близько до країв і ще не відвідана"""
    max_attempts = 100
    for _ in range(max_attempts):
        x = random.randint(-220, 220)
        y = random.randint(-220, 220)
        pos = (x, y)
        if pos not in logs:
            t.penup()
            t.goto(x, y)
            t.setheading(random.choice([0, 90, 180, 270]))
            t.pendown()
            print(f"🚀 Телепорт у: {pos}")
            return True
    print("⚠️ Не вдалося знайти вільну точку для телепорту")
    return False

teleport_to_random()

# Основний цикл
while True:
    # Обчислюємо наступну позицію
    heading = math.radians(t.heading())
    next_x = t.xcor() + 10 * math.cos(heading)
    next_y = t.ycor() + 10 * math.sin(heading)
    next_pos = (round(next_x, 2), round(next_y, 2))

    if -231 <= next_x <= 229 and -231 <= next_y <= 229 and next_pos not in logs:
        t.color("black")
        t.forward(10)
        logs.append(next_pos)
    else:
        # Пробуємо 4 рази повертатися і шукати новий напрям
        turned = False
        for _ in range(4):
            t.left(90)
            heading = math.radians(t.heading())
            test_x = t.xcor() + 10 * math.cos(heading)
            test_y = t.ycor() + 10 * math.sin(heading)
            test_pos = (round(test_x, 2), round(test_y, 2))
            if -231 <= test_x <= 229 and -231 <= test_y <= 229 and test_pos not in logs:
                turned = True
                break

        if not turned:
            # Якщо всі 4 напрями заблоковані — телепорт
            teleport_to_random()
