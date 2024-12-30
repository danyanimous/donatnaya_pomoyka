import os
import io
import sqlite3
import tabulate
import time

connection = sqlite3.connect("data/Stats.db")
cursor = connection.cursor()

accepted50 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 50").fetchone()[0]
summ50 = accepted50 * 50
accepted100 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 100").fetchone()[0]
summ100 = accepted100 * 100
accepted200 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 200").fetchone()[0]
summ200 = accepted200 * 200
accepted500 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 500").fetchone()[0]
summ500 = accepted500 * 500
accepted1000 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 1000").fetchone()[0]
summ1000 = accepted1000 * 1000
accepted2000 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 2000").fetchone()[0]
summ2000 = accepted2000 * 2000
accepted5000 = cursor.execute("SELECT quantity FROM accepted_bills WHERE nominal = 5000").fetchone()[0]
summ5000 = accepted5000 * 5000
acceptedAll = accepted50 + accepted100 + accepted200 + accepted500 + accepted1000 + accepted2000 + accepted5000
summAll = summ50 + summ100 + summ200 + summ500 + summ1000 + summ2000 + summ5000
print("-=-=-=-=-=-=-=-=-=-=-=-=-=-")
print("|СТАТИСТИКА ПРИНЯТЫХ КУПЮР|")
print("-=-=-=-=-=-=-=-=-=-=-=-=-=-")
print(" ")
data = [
    ['Номинал', 'Принято купюр', 'Сумма (руб)'],
    ['50 руб', accepted50, summ50],
    ['100 руб', accepted100, summ100],
    ['200 руб', accepted200, summ200],
    ['500 руб', accepted500, summ500],
    ['1000 руб', accepted1000, summ1000],
    ['2000 руб', accepted2000, summ2000],
    ['5000 руб', accepted5000, summ5000],
    ['ИТОГО', acceptedAll, summAll]
]
results = tabulate.tabulate(data)
print(results)
time.sleep(99999)


