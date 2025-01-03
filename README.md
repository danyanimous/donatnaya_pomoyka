# Donatnaya_pomoyka
Копилка на Python, работающая с купюроприёмниками CashCode (по протоколу CCNET) и ведущая учёт в базе данных sqlite

Всем привет! Наконец-то я подавил свою прокрастинацию и решил навести порядок на своём аккаунте здесь: специально под Новый Год публикую здесь уже четвёртую отдебаганную версию моей копилки на Python, работающей на библиотеках `PySerial` и `sqlite3`. Поведение данной программы схоже с моей предыдущей - ccnet_python, только здесь были устранены некоторые серьёзные проблемы (например, после снятия стекера и его установки обратно приходилось перезапускать программу для продолжения приёма купюр) и прикручена таблица SQL для хранения статистики о принятых купюрах (`nominal * quantity = summ`).

# Состав проекта
1. pomoyka.py - непосредственно программа (если, конечно, скрипт на интерпретируемом языке вообще можно назвать программой), подгружающая в себя таблицу SQL для регистрации всунутых купюр, COM-порт для бесконечно долгого опроса купюроприёмника по протоколу CCNET (от бренда CashCode) и простой LOG-файл для....логирования всех событий, отражаемых в консоли. Единственное, что Вам нужно поменять - номер порта (напр. на `'COM3'` или `'/dev/ttyUSB0'`) и скорость передачи данных (на `9600` либо `19200` в зависимости от выставленной на самом купюрнике скорости) в переменной `bv`. Далее - запускаем программу и радуемся!
2. get_stats.py - программа для вывода всей статистики из SQL в форме красивой и ровной таблицы. Отображает количество купюр каждого номинала, сумму каждого номинала и общую сумму _всей кассы_ в рублях.
3. erase_all.py - на размышление даётся 5 секунд: по истечении этого времени вся статистика в SQL будет забита нулями (очищена). Я также называю этот скрипт _инкассатором_.
4. Папка logs c файлом pomoyka.log внутри - вышеупомянутый файл, в который дублируется всё то, что выводилось в консоль, но с дополнительной меткой времени с точностью до миллисекунд. Рекомендуется периодически удалять его, чтобы программа не занимала уж очень много места. ***TO DO: разделение логов по дням и удаление файлов свыше указанного пользователем срока давности.***
5. Папка data с файлом Stats.db внутри - база данных (простая таблица) SQL из двух столбцов и десятка строк "`номинал | количество`". Как вы уже поняли, в ней хранится количество каждого внесённого номинала.

# Требования (библиотеки)
- sqlite3 #работа с БД
- pyserial #работа с COM-портом
- datetime #ведение лога с датировкой
- tabulate #красивый вывод статистики

p.s. За минимальную рабочую версию Python ничего сказать не могу; сама программа разрабатывалась и тестировалась (причём на настоящем платёжном терминале) на версии 3.10.11

# Принцип работы
Если у вас нет желания и/или возможности разбираться в моих костылях внутри `.py` файлов, то сейчас я вкратце объясню принцип работы программы, а именно - `pomoyka.py`:
1. Происходит импорт базы данных и лог-файла, подключение к COM-порту
2. Разово опрашивается и перезагружается купюроприёмник
3. Купюроприёмник ещё несколько раз опрашивается программой, пока не выдаст статус DISABLED, после которого программа даст команду на разрешение приёма купюр
4. Запускается бесконечный цикл, вызывающий раз в 400 миллисекунд функцию опроса купюрника, и в зависимости от ответов последнего цикл делает разные вещи (выводит сообщения в консоль, записывает новую купюру в БД или ещё много хрен знает чего)
5. Если купюрник по какой-либо причине не принял купюру, какое-то время в консоль и лог-файл будет спамить сообщением об ошибке. _**TO DO: сделать запоминание ошибки и выводить её только один раз, либо наконец перепрошить купюроприёмник, чтобы он не зависал на ~10 сек после ошибки.**_ На купюрниках с новой прошивкой спамить должно значительно меньше, ибо новая прошивка раздупляется сразу после извлечения "фальшивой" купюры.
6. Если была снята кассета, программа всего один раз выведет соответствующее сообщение в консоль, после чего будет в тихую опрашивать устройство и ждать установки кассеты на место: это так же выведет всего одно сообщение и перезагрузит кэшкод.

# Дерзайте!
На этом всё. Надеюсь, моё объяснение было понятным. Код программы открыт для всех, поэтому никто не запрещает разобраться в нём самостоятельно и/или переписать всё с меньшим количеством строк и экономным использованием ресурсов компьютера. Если вы всерьёз хотите улучшить данный проект (доработать ранее упомянутые косяки или тотально его оптимизировать) - милости прошу в форки/contribute или....честно, пока не разобрался, что есть что...
