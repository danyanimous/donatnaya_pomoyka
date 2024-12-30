import os
import io
import sqlite3
import serial
import time

connection = sqlite3.connect("data/Stats.db") #прикручиваем БД
cursor = connection.cursor()

nominals = ['50', '100', '200', '500', '1000', '2000', '5000']

print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 5')
time.sleep(1)
print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 4')
time.sleep(1)
print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 3')
time.sleep(1)
print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 2')
time.sleep(1)
print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 1')
time.sleep(1)
print('ОБНУЛЕНИЕ ВСЕЙ СТАТИСТИКИ ЧЕРЕЗ 0')
for nominal in nominals:
    cursor.execute(f"UPDATE accepted_bills SET quantity = 0 WHERE nominal = {nominal}")
    connection.commit()
    continue
print("Вся статистика успешно обнулена. Нажмите любую клавишу, чтобы выйти. (нет)")
time.sleep(99999)
