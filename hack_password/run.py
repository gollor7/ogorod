import time
from itertools import product
from multiprocessing import Pool, cpu_count
import random
import sys  # Для завершення програми

# Створюємо алфавіт: цифри + літери
alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"

# Генеруємо випадковий пароль довжиною від 4 до 5 символів
pass_length = random.randint(4, 5)
password = ''.join(random.choice(alphabet) for _ in range(pass_length))

# Функція для генерації комбінацій
def generate_combinations(length_and_password):
    length, password, start_time = length_and_password
    # Генерація всіх можливих комбінацій
    for combination in product(alphabet, repeat=length):
        key = "".join(combination)  # Об'єднуємо комбінацію в рядок
        print(key)  # Виводимо комбінацію
        if key == password:
            end_time = time.time()  # Час після знаходження пароля
            elapsed_time = end_time - start_time  # Час, який пройшов
            print(f"Пароль знайдений: {key}")
            print(f"Час, за який пароль знайдено: {elapsed_time:.2f} секунд")
            sys.exit()  # Завершуємо програму, якщо знайдений пароль

if __name__ == "__main__":
    start_time = time.time()  # Початковий час для обчислення

    # Встановлюємо кількість процесів в пулі
    num_workers = cpu_count()  # Використовуємо всі доступні ядра
    # Якщо ви хочете використовувати більше ядер, можна збільшити це значення
    # Наприклад, щоб використовувати вдвічі більше процесів:
    # num_workers = cpu_count() * 2

    # Задаємо максимальну довжину комбінацій
    max_length = pass_length  # Використовуємо довжину пароля

    # Створюємо список кортежів для передачі до процесів
    lengths_and_passwords = [(length, password, start_time) for length in range(1, max_length + 1)]

    # Створюємо пул процесів і розбиваємо роботу на окремі задачі для кожної довжини
    with Pool(num_workers) as pool:
        pool.map(generate_combinations, lengths_and_passwords)

    end_time = time.time()  # Час після завершення всього процесу
    print(f"\nЧас виконання: {end_time - start_time:.2f} секунд")
