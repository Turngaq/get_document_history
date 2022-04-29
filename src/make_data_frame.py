import os
import pandas as pd
import re


# Создает датафрейм из текстового файла
def make_history_data_frame(file_path):
    history_df = pd.DataFrame({
        'Date': [],
        'Time': [],
        'Type': [],
        'Button': [],
        'Action': [],
        'UserId': [],
    })
    if os.path.exists(file_path) and os.path.isfile(file_path):
        file = open(file_path, 'r')

        for index, line in enumerate(file, 0):
            # print('currentLine: ' + str(index))
            date = line[:10]
            time = line[11:23]
            note_type = 'UNKNOWN'
            if re.search('ERROR', line) is not None:
                note_type = 'ERROR'
            elif re.search('INFO', line) is not None:
                note_type = 'INFO'
            elif re.search('DEBUG', line) is not None:
                note_type = 'DEBUG'

            button_id = get_id(line, '-action-')
            action_description = get_description(line)
            user_id = get_id(line, "user', id: '")
            history_df.loc[index] = [date, time, note_type, button_id, action_description, user_id]

        file.close()
    else:
        print('file: ' + file_path + ' - not found')
    return history_df


def get_id(line, after_word):
    result = ''
    i = line.find(after_word) + len(after_word)
    while line[i].isnumeric():
        result = result + line[i]
        i = i + 1
    return result


def get_name(line, after_word):
    result = ''
    i = line.find(after_word) + len(after_word)
    while line[i] != '\'':
        result = result + line[i]
        i = i + 1
    return result


def get_description(line):
    if re.search('Requested view:', line) is not None:
        return 'Requested view'
    elif re.search('fireEvent:', line) is not None:
        return get_name(line, "fireEvent: '") + ' ' + get_name(line, "connector: '")
    elif re.search('Cannot determine access', line) is not None:
        return 'Cannot determine access'
    else:
        return 'UNKNOWN'
