from math import sqrt

a = int(input('Введіть a: '))
b = int(input('Введіть b: '))
c = int(input('Введіть c: '))

discriminant = b ** 2 - 4*(a*c)
if discriminant < 0:
    print('Рівняння не має дійсних коренів')
else:
    x1 = (-b - sqrt(discriminant)) / 2*a
    x2 = (-b + sqrt(discriminant)) / 2*a

    print(f'x1: {x1}\nx2: {x2}')