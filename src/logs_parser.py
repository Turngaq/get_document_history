import os
import configparser
import glob
import subprocess
import pandas as pd

import src.make_data_frame as make_data_frame

RESULT_TEXT_FILE_NAME = 'history_result'


# сформировать строку документа из его составляющих
def form_document_string(document_id, document_type_id, document_version_id):
    return "(typeId: '" + str(document_type_id) + "', id: '" + str(document_id) + "', versionId: '" + str(
        document_version_id) + "')"


# искать строку в файле по ключевому слову и вернуть найденое содержимое
def find_str(key_word, file_path):
    if os.path.exists(file_path) is True:
        try:
            resByteArr = subprocess.check_output('findstr /c:"' + key_word + '" ' + file_path)
            print("read from " + file_path + " successfully")
            return resByteArr
        except subprocess.CalledProcessError:
            print("no such str in " + file_path + ".")
    else:
        print('file "' + file_path + '" - not found')
    return ''.encode('utf-8')


# находит все строки во всех файлах в выбранной дирректории по ключевому слову, записывает в файл
def find_str_in_path(key_word, search_dir_path, result_file_path):
    # clean result file
    if os.path.exists(result_file_path):
        os.remove(result_file_path)
    result_file = open(result_file_path, 'a')
    # find in path
    if os.path.exists(search_dir_path) and os.path.isdir(search_dir_path):
        file_names_list = os.listdir(search_dir_path)
        if len(file_names_list) == 0:
            print('no Files in Dir: "' + search_dir_path + '"')
        for fileName in file_names_list:
            search_file_path = search_dir_path + '\\' + fileName
            result_file.write(find_str(key_word, search_file_path).decode('utf-8'))
    else:
        print('directory: "' + search_dir_path + '" - not found')
    result_file.close()


# удалить все строки содержащие ключевое слово и вернуть содержимое
def remove_string(key_word, file_path):
    if os.path.exists(file_path) is True:
        try:
            resByteArr = subprocess.check_output('findstr /v /c:"' + key_word + '" ' + file_path)
            print("read from " + file_path + " successfully")
            return resByteArr
        except subprocess.CalledProcessError:
            print("no such str in " + file_path + ".")
    else:
        print('file "' + file_path + '" - not found')
    return ''.encode('utf-8')


# сохраняет строку в файл
def save_string_in_file(string, file_path):
    result_file = open(file_path, 'w')
    result_file.write(string.decode('utf-8'))
    result_file.close()


# удаляет пустые строки из файла
def removeBlankLines(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            if not line.isspace():
                lines.append(line)
    with open(file_path, 'w') as f:
        f.writelines(lines)


# создает файл history_result в временной директории с записями о действиях пользователя на форме
def create_history_result_text(document, logs_path, tmp_path):
    find_str_in_path(document, logs_path, os.path.join(tmp_path, RESULT_TEXT_FILE_NAME))
    save_string_in_file(
        find_str('user', os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)),
        os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)
    )
    save_string_in_file(
        find_str('action-', os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)),
        os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)
    )
    save_string_in_file(
        remove_string('fire event param:', os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)),
        os.path.join(tmp_path, RESULT_TEXT_FILE_NAME)
    )
    removeBlankLines(os.path.join(tmp_path, RESULT_TEXT_FILE_NAME))


def get_document_history(config_path, document_id, document_type_id, document_version_id):
    print('Старт проверок...')

    # проверки и чтение конфига
    if document_version_id == '':
        document_version_id = '1'

    if document_type_id == '':
        print('Нужно указать и ID и TYPE_ID')
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.abspath(config_path)):
        print('Конфиг не найден, задайте настройки')
        print('Поиск истории закончен')
        return

    config = configparser.ConfigParser()
    config.read(config_path)
    logs_path = config.get('settings', 'logs_path')
    result_path = config.get('settings', 'result_path')
    tmp_path = config.get('settings', 'tmp_path')
    csv_path = config.get('settings', 'csv_path')

    if not os.path.exists(os.path.abspath(csv_path)):
        print('Не найдена директория csv_files: ' + os.path.abspath(csv_path))
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.join(os.path.abspath(csv_path), 'buttons.csv')):
        print('Не найден buttons.csv в директории: ' + os.path.abspath(csv_path))
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.join(os.path.abspath(csv_path), 'forms.csv')):
        print('Не найден forms.csv в директории: ' + os.path.abspath(csv_path))
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.join(os.path.abspath(csv_path), 'users.csv')):
        print('Не найден users.csv в директории: ' + os.path.abspath(csv_path))
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.abspath(logs_path)):
        print('Не найден путь до директории: ' + os.path.abspath(logs_path))
        print('Поиск истории закончен')
        return

    if not os.path.exists(os.path.abspath(result_path)):
        print('Не найдена директория для сохранения результата: ' + os.path.abspath(result_path))
        print('Поиск истории закончен')
        return

    print('Проверки пройдены')

    print('Начато чтение из логов...')
    if not os.path.exists(os.path.abspath(tmp_path)):
        os.mkdir(os.path.abspath(tmp_path))
        print('created tmp path')
    else:
        files = glob.glob(os.path.join(os.path.abspath(tmp_path), '*'))
        for f in files:
            os.remove(f)

    document = form_document_string(str(document_id), str(document_type_id), str(document_version_id))
    print('document: ' + document)

    # создание файла с историческими записями из лога
    create_history_result_text(
        document,
        os.path.abspath(logs_path),
        os.path.abspath(tmp_path),
    )

    # формирование датафрейма
    history_df = make_data_frame.make_history_data_frame(os.path.join(tmp_path, RESULT_TEXT_FILE_NAME))
    users_df = pd.read_csv(os.path.join(csv_path, 'users.csv'), encoding='utf-8')
    buttons_df = pd.read_csv(os.path.join(csv_path, 'buttons.csv'))
    forms_df = pd.read_csv(os.path.join(csv_path, 'forms.csv'))

    history_df['UserId'] = history_df['UserId'].astype(int)
    history_df['Button'] = history_df['Button'].astype(int)

    mergedDf = history_df.merge(users_df, left_on='UserId', right_on='id')
    mergedDf = mergedDf.merge(buttons_df, left_on='Button', right_on='ButtonId')
    mergedDf = mergedDf.merge(forms_df, left_on='FormId', right_on='FormId')

    result_df = pd.DataFrame({
        'Дата': mergedDf['Date'],
        'Время': mergedDf['Time'],
        'Имя кнопки': mergedDf['ButtonTitle'],
        'Описание кнопки': mergedDf['ButtonDescription'],
        'Описание формы': mergedDf['FormDescription'],
        'ФИО': mergedDf['fio']
    })

    excel_file_name = 'history_' + document_type_id + '_' + document_id + '_' + document_version_id + '.xlsx'

    # удаление старого файла с результатами
    if os.path.exists(os.path.join(result_path, excel_file_name)):
        os.remove(os.path.join(result_path, excel_file_name))

    # запись нового файла с результатами
    with pd.ExcelWriter(os.path.join(result_path, excel_file_name)) as writer:
        result_df.to_excel(writer, index=False)

    print('Сформирован файл: ' + os.path.join(result_path, excel_file_name))
    print('Поиск истории закончен')

    return
