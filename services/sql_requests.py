from psycopg2 import connect
from config_data.config import Config, load_config
from datetime import datetime


# Загружаем конфиг в переменную config
config: Config = load_config()


# Создаем соединение с БД
def get_connect_to_db():
    '''Функция создания соединения с БД'''
    try:
        return connect(f'postgresql://{config.tg_db.user}:{config.tg_db.password}@{config.tg_db.host}/{config.tg_db.dbname}')
    except:
        print('Не удалось соединиться с БД')


# Получение списка ID админов из БД
def get_admin_IDs():
    '''Функция возваращает список ID администраторов бота. -> [int,]'''
    conn = get_connect_to_db() # Открываем соединение с БД  
    # Делаем запрос на получение списка всех пользователей
    with conn.cursor() as curs:
        curs.execute('''SELECT tg_user_id
                        FROM users
                        JOIN roles USING(role_id)
                        WHERE role_name = 'admin' AND remove = FALSE  
                     ''')
        result = curs.fetchall()
    conn.close() # закрываем соединение
    tg_admins = []
    for user in result:
        tg_admins.append(user[0])
    return tg_admins # возвращаем список ID админов


# Получение списка ID супер_админов из БД
def get_superadmin_IDs():
    '''Функция возваращает список ID супер-администраторов бота. -> [int,]'''
    conn = get_connect_to_db() # Открываем соединение с БД
    # Делаем запрос на получение списка всех пользователей
    with conn.cursor() as curs:
        curs.execute('''SELECT tg_user_id
                        FROM users
                        JOIN roles USING(role_id)
                        WHERE role_name = 'superadmin' AND remove = FALSE 
                     ''')
        result = curs.fetchall()
    conn.close() # закрываем соединение
    tg_superadmins = []
    for user in result:
        tg_superadmins.append(user[0])
    return tg_superadmins # возвращаем список ID суперадминов


# Получение списка ID пользователей без привилегий из БД
def get_user_IDs():
    '''Функция возваращает список ID обычных пользователей бота. -> [int,]'''
    conn = get_connect_to_db() # Открываем соединение с БД
    # Делаем запрос на получение списка всех пользователей
    with conn.cursor() as curs:
        curs.execute('''SELECT tg_user_id
                        FROM users
                        JOIN roles USING(role_id)
                        WHERE role_name = 'user' AND remove = FALSE   
                     ''')
        result = curs.fetchall()
    conn.close() # закрываем соединение
    tg_users = []
    for user in result:
        tg_users.append(user[0])
    return tg_users # возвращаем список ID обычных пользователей


# Получение списка ID всех удаленных пользователей из БД
def get_all_deleted_users_IDs():
    '''Функция возваращает список ID обычных пользователей бота. -> [int,]'''
    conn = get_connect_to_db() # Открываем соединение с БД
    # Делаем запрос на получение списка всех пользователей
    with conn.cursor() as curs:
        curs.execute('''SELECT tg_user_id, 
                        FROM users
                        JOIN roles USING(role_id)
                        WHERE remove = TRUE
                     ''')
        result = curs.fetchall()
    conn.close() # закрываем соединение
    tg_users = []
    for user in result:
        tg_users.append(user[0])
    return tg_users # возвращаем список ID обычных пользователей


# Функция поиска пользователя по tg_user_id
def find_user(tg_user_id: int):
    '''На вход функции подается ID пользователя для поиска его в БД и 
    возвращается результат в виде списка. -> [int, str, str, str, boolean]'''
    conn = get_connect_to_db() # Открываем соединение с БД
    # Делаем запрос на получение списка всех пользователей
    with conn.cursor() as curs:
        curs.execute('''SELECT DISTINCT tg_user_id, user_name, role_name, remove
                        FROM users
                        JOIN roles USING(role_id)
                        WHERE tg_user_id=''' + str(tg_user_id)
                    )
        tg_user = curs.fetchone()
    conn.close() # закрываем соединение
    return tg_user # возвращаем список с информацией о пользователе


# Функция добавления пользователя бота
def add_user(user_name: str, tg_user_id: int, role: str):
    '''Функция добавляет в БД пользователя.
    Возвращается сообщение пользователю о совершенной операции'''
    conn = get_connect_to_db() # Открываем соединение с БД
    found = find_user(tg_user_id)
    msg: str = 'Функция по непонятным причинам не отработала'
    if not found:
        with conn.cursor() as curs:
            curs.execute('''INSERT INTO public.users(user_name, tg_user_id, role_id)
                        VALUES ( ''' +"'"+ user_name +"'"+ ''', 
                                ''' + str(tg_user_id) + ''', 
                                (SELECT role_id FROM public.roles WHERE role_name = ''' +"'"+ role +"'"+ '''))''')
        msg = 'Пользователь добавлен как новый'
    elif found and found[-1] == True:
        with conn.cursor() as curs:
            curs.execute('''UPDATE public.users
                        SET user_name=''' +"'"+ user_name +"'"+ ''', 
                            tg_user_id=''' + str(tg_user_id) + ''',
                            role_id=(SELECT role_id FROM public.roles WHERE role_name = ''' +"'"+ role +"'"+ '''), 
                            remove=FALSE
                        WHERE tg_user_id=''' + str(tg_user_id))
        msg = 'Пользователь восстановлен из удаленных'
    else:
        msg = 'Такой пользователь уже существует'
    conn.commit() # записываем данные в таблицу
    conn.close() # закрываем соединение
    return msg # Возвращаем сообщение о результате добавления пользователя


# Функция удаления пользователя бота
def del_user(tg_user_id: int):
    '''Функция помечает пользователя как удаленный.
    Возвращается сообщение пользователю о результате.'''
    conn = get_connect_to_db() # Открываем соединение с БД
    msg: str = 'Функция по непонятным причинам не отработала' 
    found = find_user(tg_user_id)
    if found and found[-1] == False:
        with conn.cursor() as curs:
            curs.execute('''UPDATE public.users
                        SET remove=TRUE
                        WHERE tg_user_id=''' + str(tg_user_id))
        msg = 'Пользователь удален'
    elif found and found[-1] == True:
        msg = 'Такой пользователь уже был удален'
    else:
        msg = 'Такой пользователь не найден'
    conn.commit() # записываем данные в таблицу
    conn.close() # закрываем соединение
    return msg # Возвращаем сообщение пользователю о результате


# Фукнция проверки прав админа
def is_admin(user: int):
    '''Фукция проверяет, входит ли пользователь в группы администраторов'''
    admins: list[int] = get_admin_IDs() # Получение списка админов
    super_admins: list[int] = get_superadmin_IDs() # Получение списка суперадминов
    if user in admins or user in super_admins:
        return True
    else:
        return False
    

# Фукнция проверки? является ли пользователем
def is_user(user: int):
    '''Фукция проверяет, входит ли контакт в группу пользователей'''
    users: list[int] = get_user_IDs() # Получение из конфига списка обычных пользователей
    if user in users:
        return True
    else:
        return False
    
    
 # Получение списка шаблонов 
def get_patterns(type_pattern: str):
    '''Функция возвращает список шаблонов. 
    В качестве аргумента передается тип: certificate или diploma'''
    conn = get_connect_to_db() # Открываем соединение с БД
    with conn.cursor() as curs:
        curs.execute('''
                    SELECT type_id, type_name, pattern_url
                    FROM '''+type_pattern+'''_types
                    WHERE remove = FALSE
                    ''')
        result = curs.fetchall()
    conn.close()
    return result # Список шаблонов


# Добавление подарочного сертификата в БД
def add_gift(number: str, client: str, type_id: str, course: str, tg_user_id: int, date: str):
    '''Функция добавляет в БД сертификат'''
    conn = get_connect_to_db() # Открываем соединение с БД
    
    with conn.cursor() as curs:
        curs.execute('''
                    SET datestyle = dmy;
                    INSERT INTO public.certificates(
                        number, client, type_id, course, user_id, date 
                    )
                    VALUES (
                        ''' +"'"+ number +"'"+ ''',
                        ''' +"'"+ client +"'"+ ''',
                        ''' +"'"+ type_id +"'"+ ''',
                        ''' +"'"+ course +"'"+ ''',
                        (SELECT user_id FROM users WHERE tg_user_id = ''' + str(tg_user_id) + '''),
                        ''' +"'"+ date +"'"+ '''
                    )
                    RETURNING certificate_id
                     ''')
        result = curs.fetchall()[0][0]
    conn.commit()   # записываем в БД
    conn.close()    # закрываем соединение
    return result   # ID добавленной записи


# Добавление аттестата в БД
def add_doc(number: str, client: str, type_id: str, course: str, tg_user_id: int, date: str):
    '''Функция добавляет в БД итогового аттастата'''
    conn = get_connect_to_db() # Открываем соединение с БД
    
    with conn.cursor() as curs:
        curs.execute('''
                    SET datestyle = dmy;
                    INSERT INTO public.diplomas(
                        number, client, type_id, course, user_id, date 
                    )
                    VALUES (
                        ''' +"'"+ number +"'"+ ''',
                        ''' +"'"+ client +"'"+ ''',
                        ''' +"'"+ type_id +"'"+ ''',
                        ''' +"'"+ course +"'"+ ''',
                        (SELECT user_id FROM users WHERE tg_user_id = ''' + str(tg_user_id) + '''),
                        ''' +"'"+ date +"'"+ '''
                    )
                    RETURNING diploma_id
                     ''')
        result = curs.fetchall()[0][0]
    conn.commit()   # записываем в БД
    conn.close()    # закрываем соединение
    return result   # ID добавленной записи


# Поиск подарочного сертификата в БД
def find_gift(phone: str | None = None, name: str | None = None, id: int | None = None):
    '''Функция ищет подарочный сертификат по:
     Если задано phone - последним 4 цифрам его номера;
     Если задано name  - по имени клиента;
     Если задано id    - по ID сертификата.'''
    conn = get_connect_to_db() # Открываем соединение с БД
    if phone:
        with conn.cursor() as curs:
            curs.execute('''SELECT number, client, course, user_name
                        FROM public.certificates AS c
                        JOIN users USING(user_id)
                        WHERE c.remove = FALSE AND number LIKE '%''' + phone + ''''
                        ''')
            result = curs.fetchall()
    elif name:
        with conn.cursor() as curs:
            curs.execute('''SELECT number, client, course, user_name
                        FROM public.certificates AS c
                        JOIN users USING(user_id)
                        WHERE c.remove = FALSE AND client LIKE '%''' + name + '''%'
                        ''')
            result = curs.fetchall()
    elif id:
        with conn.cursor() as curs:
            curs.execute('''SELECT number, client, course, pattern_url
                        FROM public.certificates AS c
                        JOIN certificate_types USING(type_id)
                        WHERE c.remove = FALSE AND certificate_id =''' + str(id)
                        )
            result = curs.fetchone()
    else:
        result = []
        print('Зашел в ловушку')
    conn.close()    # закрываем соединение
    return result   # Возвращает словарь всех сертификатов

# Поиск итогового аттестата в БД
def find_docs(id: int):
    '''Функция ищет итоговый аттестат по ID сертификата.'''
    conn = get_connect_to_db() # Открываем соединение с БД
    with conn.cursor() as curs:
            curs.execute('''SELECT number, client_ru, client_en, course_ru, course_en, pattern_url, date, hours
                        FROM public.diplomas AS d
                        JOIN diploma_types USING(type_id)
                        WHERE d.remove = FALSE AND diploma_id =''' + str(id)
                        )
            result = curs.fetchone()
    conn.close()    # закрываем соединение
    return result   # Возвращает словарь всех сертификатов


# Фукнция поиска номера последнего аттестат
def last_docs_number():
    '''Фукция возвращает номер последнего выданного аттестата'''
    conn = get_connect_to_db() # Открываем соединение с БД
    with conn.cursor() as curs:
            curs.execute('''SELECT number
                         FROM diplomas
                         ORDER BY diploma_id DESC
                         LIMIT 1
                        ''')
            result = curs.fetchone()
    conn.close()    # закрываем соединение
    if result:
        return result[0]   # Возвращает номер
    else:
        return '00000'


    
    
