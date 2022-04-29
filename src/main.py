import PySimpleGUI as sg
import configparser
import os
import threading
import pandas as pd
import glob
from datetime import datetime

import src.forms_parser as forms_parser
import src.logs_parser as logs_parser

CONFIG_PATH = './settings.ini'
CSV_PATH = './csv_files/'
TMP_PATH = './src/tmp_files/'
THREAD_EVENT = '-THREAD-'


def update_buttons_and_forms(forms_path, window):
    if not os.path.exists(os.path.abspath(forms_path)):
        print('I can\'t find the forms path: ' + os.path.abspath(forms_path))
        # window.write_event_value(THREAD_EVENT, (threading.current_thread().name, 'err'))
        window.write_event_value(THREAD_EVENT, 'err')
        return

    if not os.path.exists(os.path.abspath(CSV_PATH)):
        os.mkdir(os.path.abspath(CSV_PATH))
        print('created created path: ' + os.path.abspath(CSV_PATH))

    # получение данных кнопок и форм
    formsList = glob.glob(forms_path + '/**/*.view', recursive=True)
    length = len(formsList)
    forms_df = pd.DataFrame({
        'FormId': [],
        'FormTSHort': [],
        'FormDescription': []
    })
    buttons_df = pd.DataFrame({
        'ButtonId': [],
        'ButtonName': [],
        'ButtonTitle': [],
        'ButtonDescription': [],
        'ButtonTransferType': [],
        'ButtonTransferAddress': [],
        'FormId': []
    })
    i = 1
    for fileName in formsList:
        print(str(i) + '/' + str(length) + ' | trying form: ' + str(fileName))
        forms_parser.get_form_data(fileName, forms_df)
        forms_parser.get_buttons_data(fileName, buttons_df)
        i = i + 1

    forms_df.to_csv(CSV_PATH + 'forms.csv', encoding='utf-8')
    buttons_df.to_csv(CSV_PATH + 'buttons.csv', encoding='utf-8')
    window.write_event_value(THREAD_EVENT, 'end')


def get_document_history_and_send_event(window, document_id, document_type_id, document_version_id):
    logs_parser.get_document_history(CONFIG_PATH, document_id, document_type_id, document_version_id)
    window.write_event_value(THREAD_EVENT, 'end')


def save_settings(log_path, forms_path, result_path, refresh_info_date):
    print('Saving settings...')
    if log_path == '':
        print('WARNING! EMPTY log_path VALUE SAVED')
    if forms_path == '':
        print('WARNING! EMPTY forms_path VALUE SAVED')
    if result_path == '':
        print('WARNING! EMPTY result_path VALUE SAVED')
    config = configparser.ConfigParser()
    config.add_section('settings')
    config.add_section('info')
    config.set('settings', 'logs_path', log_path)
    config.set('settings', 'forms_path', forms_path)
    config.set('settings', 'result_path', result_path)
    config.set('settings', 'tmp_path', TMP_PATH)
    config.set('settings', 'csv_path', CSV_PATH)
    config.set('info', 'refresh_info_date', refresh_info_date)
    with open(CONFIG_PATH, "w") as config_file:
        config.write(config_file)
    print('Settings saved...')


def open_settings_window():
    logs_path = ''
    forms_path = ''
    result_path = '../'
    refresh_info_date = 'Никогда'
    if os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        logs_path = config.get('settings', 'logs_path')
        forms_path = config.get('settings', 'forms_path')
        result_path = config.get('settings', 'result_path')
        refresh_info_date = config.get('info', 'refresh_info_date')

    layout = [
        [sg.Text('Путь до логов', size=(26, 0)), sg.Input(default_text=logs_path, key='LOGS_PATH')],
        [sg.Text(size=(0, 1))],
        [sg.Text('Последний раз было обновлено: ' + refresh_info_date, key='REFRESH_INFO_DATE')],
        [
            sg.Text('Путь до форм', size=(26, 0)), sg.Input(default_text=forms_path, key='FORMS_PATH'),
            sg.Button(button_text='Обновить', key='REFRESH_BUTTONS_AND_FORMS_INFO'),
        ],
        [sg.Text('Чтобы получить данные о кнопках. Например: C:/project/meta/src/main/forms')],
        [sg.Text(size=(0, 1))],
        [sg.Text('Путь до папки с результатами', size=(26, 0)), sg.Input(default_text=result_path, key='RESULT_PATH')],
        [sg.Text(size=(0, 1))],
        [
            sg.Button(button_text='Сохранить', key='SAVE_SETTINGS'),
            sg.Button(button_text='Закрыть', key='CLOSE_SETTINGS')
        ],
        [sg.Text(size=(0, 1))],
        [sg.Text('Output', font='Any 15')],
        [sg.Multiline(size=(74, 10), key='-ML_settings-', autoscroll=True, reroute_stdout=True, write_only=True,
                      reroute_cprint=True)],
    ]

    window = sg.Window('Настройки', layout, modal=True)
    while True:
        event, values = window.read()
        if event == 'CLOSE_SETTINGS' or event == sg.WIN_CLOSED:
            break
        if event == 'SAVE_SETTINGS':
            save_settings(
                str(values['LOGS_PATH']),
                str(values['FORMS_PATH']),
                str(values['RESULT_PATH']),
                refresh_info_date
            )
            break
        if event == 'REFRESH_BUTTONS_AND_FORMS_INFO':
            if str(values['FORMS_PATH']) == '':
                print('empty forms directory')
            else:
                try:
                    window['REFRESH_BUTTONS_AND_FORMS_INFO'].update(disabled=True)
                    window['SAVE_SETTINGS'].update(disabled=True)
                    window['CLOSE_SETTINGS'].update(disabled=True)
                    threading.Thread(
                        target=update_buttons_and_forms,
                        args=(str(values['FORMS_PATH']), window),
                        daemon=True,
                    ).start()
                except Exception as e:
                    sg.popup_error(f'AN EXCEPTION OCCURRED!', e)

        if event == THREAD_EVENT:
            if values[THREAD_EVENT] == 'end':
                # обновление данных настроек и даты последнего обновления, после его завершения
                refresh_info_date = str(datetime.now())
                window['REFRESH_INFO_DATE'].update('Последний раз было обновлено: ' + refresh_info_date)
                save_settings(
                    str(values['LOGS_PATH']),
                    str(values['FORMS_PATH']),
                    str(values['RESULT_PATH']),
                    refresh_info_date
                )
            window['REFRESH_BUTTONS_AND_FORMS_INFO'].update(disabled=False)
            window['SAVE_SETTINGS'].update(disabled=False)
            window['CLOSE_SETTINGS'].update(disabled=False)

    window.close()


def main() -> object:
    layout = [
        [sg.Text(text='', size=(74, 2)), sg.Button('Настройки', key='SETTINGS')],
        [sg.Text(text='ID', size=(26, 0)), sg.Text(text='TYPE_ID', size=(26, 0)),
         sg.Text(text='VERSION_ID', size=(26, 0))],
        [sg.Input(key='document_id', size=(30, 0), focus=True),
         sg.Input(key='document_type_id', size=(30, 0)),
         sg.Input(key='document_version_id', size=(30, 0))],
        [sg.Text(text='', size=(26, 2))],
        [sg.Text(text='', size=(26, 0)), sg.Button('Поиск', key='SEARCH', size=(26, 2))],
        [sg.Text(text='', size=(26, 2))],
        [sg.Text('Output', font='Any 15')],
        [sg.Multiline(size=(95, 10), key='ML', autoscroll=True, reroute_stdout=True, write_only=True,
                      reroute_cprint=True)],
    ]

    window = sg.Window('Document history', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            break
        if event == 'SETTINGS':
            open_settings_window()
            window['ML'].reroute_stdout_to_here()
        if event == 'SEARCH':
            try:
                window['SEARCH'].update(disabled=True)
                window['SETTINGS'].update(disabled=True)
                threading.Thread(
                    target=get_document_history_and_send_event,
                    args=(
                        window,
                        str(values['document_id']),
                        str(values['document_type_id']),
                        str(values['document_version_id']),
                    ),
                    daemon=True,
                ).start()
            except Exception as e:
                sg.popup_error(f'AN EXCEPTION OCCURRED!', e)
        if event == THREAD_EVENT:
            window['SEARCH'].update(disabled=False)
            window['SETTINGS'].update(disabled=False)