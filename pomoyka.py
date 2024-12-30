import io
import sqlite3
import serial
from datetime import datetime
import time

connection = sqlite3.connect('data/Stats.db')
cursor = connection.cursor()
bv = serial.Serial('COM2', 9600)
nominals = ['50', '100', '200', '500', '1000', '2000', '5000']
isStackerRemoved = 0

command_poll = b'\x02\x03\x06\x33\xDA\x81'
command_reset = b'\x02\x03\x06\x30\x41\xb3'
command_enable = b'\x02\x03\x0C\x34\xFF\xFF\xFF\x00\x00\x00\xB5\xC1'
command_disable = b'\x02\x03\x0C\x34\x00\x00\x00\x00\x00\x00\xB5\xC1'
ack = b'\x02\x03\x06\x00\xC2\x82'

def cashcode_reset():
    bv.write(command_reset)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Перезагрузка купюроприёмника...')
        wlog('Перезагрузка купюроприёмника...')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        wlog(f'Вместо ожидаемого АСК мы получили...  {bv.read(bv.in_waiting)}')
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить

def cashcode_enable():
    bv.write(command_enable)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Приём купюр разрешён.')
        wlog('Приём купюр разрешён.')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        wlog(f'Вместо ожидаемого АСК мы получили...  {bv.read(bv.in_waiting)}')
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить

def cashcode_disable():
    bv.write(command_disable)
    time.sleep(0.02)
    if bv.read(bv.in_waiting) == ack:
        print('Приём купюр запрещён.')
        wlog('Приём купюр запрещён.')
    else:
        print('Вместо ожидаемого АСК мы получили... ', bv.read(bv.in_waiting))
        wlog(f'Вместо ожидаемого АСК мы получили...  {bv.read(bv.in_waiting)}')
        bv.write(ack)
        if bv.in_waiting > 0:
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить

def cashcode_poll():
    bv.write(command_poll)
    time.sleep(0.02)
    global isStackerRemoved
    if bv.read(2) == b'\x02\x03': #значит пришло что-то именно от кэшкода (а не какая-либо помеха)
        bv.read(1) #считываем длину пакета "в никуда"
        status = bv.read(1)
        if status == b'\x13': #статус INITIALIZING
            bv.write(ack)
            print('Купюроприёмник успешно перезагружен!')
            wlog('Купюроприёмник успешно перезагружен!')
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x19':
            bv.write(ack)
            print('Купюроприёмник пока что заблокирован.')
            wlog('Купюроприёмник пока что заблокирован.')
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
            if isStackerRemoved == 1: #если мы находим, что недавно был снят стекер
                print('Кассета на месте, включаю купюроприёмник...')
                isStackerRemoved = 0 #сбрасываем значение на ноль
                time.sleep(0.5)
                cashcode_enable() #и обратно включаем купюрник
        elif status == b'\x14':
            bv.write(ack)
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x15':
            bv.write(ack)
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x17':
            bv.write(ack)
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x44': #JAM IN STACKER
            bv.write(ack)
            print('ОШИБКА: Замятие/застревание купюры в стекере.')
            wlog('ОШИБКА: Замятие/застревание купюры в стекере.')
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x43': #JAM IN ACCEPTOR
            bv.write(ack)
            print('ОШИБКА: Замятие/застревание купюры в купюроприёмнике.')
            wlog('ОШИБКА: Замятие/застревание купюры в купюроприёмнике.')
            bv.read(bv.in_waiting) #очищаем буфер
        elif status == b'\x42':
            bv.write(ack)
            if isStackerRemoved == 0: #если стекер до этого был на месте (его только что сняли)
                isStackerRemoved = 1 #отмечаем данное событие и не срём в логи сотни строк об ошибке
                print('ОШИБКА: Снята кассета.')
                wlog('ОШИБКА: Снята кассета.')
            bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
        elif status == b'\x47':
            error = bv.read(1)
            if error == b'\x55': #предположительно, возникает при откидывании крышки с датчиками
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('ОШИБКА: FAILURE 55')
                wlog('ОШИБКА: FAILURE 55')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('FAILURE с иным кодом (что оно значит - без понятия): ', error)
                wlog(f'FAILURE с иным кодом (что оно значит - без понятия): {error}')
        elif status == b'\x1c':
            print('НЕ УДАЛОСЬ РАСПОЗНАТЬ КУПЮРУ')
            wlog('НЕ УДАЛОСЬ РАСПОЗНАТЬ КУПЮРУ')
            error = bv.read(1) #считываем ещё один байт, содержащий в себе подробности ошибки
            if error == b'\x69':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('|   CAPACITY ERROR')
                wlog('|   CAPACITY ERROR')
            elif error == b'\x68':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('|   DENOMINATION INHIBITED')
                wlog('|   DENOMINATION INHIBITED')
            elif error == b'\x66':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('|   VERIFICATION ERROR')
                wlog('|   VERIFICATION ERROR')
            elif error == b'\x65':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('|   IDENTIFICATION ERROR')
                wlog('|   IDENTIFICATION ERROR')
            elif error == b'\x64':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('|   CONVEYING ERROR')
                wlog('|   CONVEYING ERROR')
            elif error == b'\x60':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('|   INSERTION ERROR')
                wlog('|   INSERTION ERROR')
            elif error == b'\x6A':
                bv.read(2) #считываем в никуда контрольную сумму
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('|   OPERATION ERROR')
                wlog('|   OPERATION ERROR')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('|   НЕИЗВЕСТНАЯ ОШИБКА: ', error)
                wlog(f'|   НЕИЗВЕСТНАЯ ОШИБКА: {error}')
        elif status == b'\x81':
            nominal = bv.read(1) #считываем следующий байт, содержащий номинал купюры
            if nominal == b'\x02':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 10 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 10')
                connection.commit()
                wlog('Принята купюра 10 рублей.')
            elif nominal == b'\x03':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 50 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 50')
                connection.commit()
                wlog('Принята купюра 50 рублей.') 
            elif nominal == b'\x04':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 100 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 100')
                connection.commit()
                wlog('Принята купюра 100 рублей.')
            elif nominal == b'\x0c':
                bv.read(2) #считываем в никуда контрольную сумму 
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер
                print('Принята купюра 200 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 200')
                connection.commit()
                wlog('Принята купюра 200 рублей.')
            elif nominal == b'\x05':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 500 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 500')
                connection.commit()
                wlog('Принята купюра 500 рублей.')
            elif nominal == b'\x06':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 1000 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 1000')
                connection.commit()
                wlog('Принята купюра 1000 рублей.')
            elif nominal == b'\x07':
                bv.read(2) #считываем в никуда контрольную сумму (НУ А НАХУЙ ОНА ВООБЩЕ НУЖНА?)))))
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра 5000 рублей.')
                cursor.execute(f'UPDATE accepted_bills SET quantity = quantity + 1 WHERE nominal = 5000')
                connection.commit()
                wlog('Принята купюра 5000 рублей.')
            else:
                bv.read(2)
                bv.write(ack)
                bv.read(bv.in_waiting) #очищаем буфер, ибо нехуй тут после АСКа флудерастить
                print('Принята купюра неизвестного номинала: ', nominal)
                wlog(f'Принята купюра неизвестного номинала: {nominal}')
        else:
            print('ПРИНЯТ НЕИЗВЕСТНЫЙ СТАТУС НЕИЗВЕСТНОГО ПРОИСХОЖДЕНИЯ: 02 03 XX', bv.read(bv.in_waiting))
    else: #если сообщение пришло от другой периферии, или это вообще мусор какой-то...
        print('Мы не знаем, что это такое. Если бы мы знали, что это такое. Мы не знаем, что это такое...', bv.read(bv.in_waiting))
        wlog(f'Мы не знаем, что это такое. Если бы мы знали, что это такое. Мы не знаем, что это такое... {bv.read(bv.in_waiting)}')


cursor.execute('CREATE TABLE IF NOT EXISTS accepted_bills(nominal  INT, quantity INT)')
for nominal in nominals:
    if cursor.execute(f"SELECT nominal FROM accepted_bills WHERE nominal = {nominal}").fetchone() is None:
        cursor.execute(f"INSERT INTO accepted_bills VALUES({nominal}, 0)")
    else:
        pass
connection.commit()

def wlog(text):
    logfile = io.open('logs/pomoyka.log', 'a', encoding = 'utf-8')
    logfile.write(f'{datetime.now()} :: {text}\n')
    logfile.close()

print(datetime.now(), 'Система "Донатная помойка (v1.4-release)" запускается...')
wlog('Система "Донатная помойка (v1.4-release)" запускается...')
time.sleep(2)
cashcode_reset()
time.sleep(5)
cashcode_poll() #INITIALIZING
time.sleep(0.2)
cashcode_poll() #DISABLED
time.sleep(0.2)
print('Включаю купюроприёмник...')
wlog('Включаю купюроприёмник...')
cashcode_enable()
time.sleep(0.2)
cashcode_poll() #IDLING

while bv.is_open:
    cashcode_poll()
    time.sleep(0.4)
        
