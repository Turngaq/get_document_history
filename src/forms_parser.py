import re


def get_form_id(file_path):
    end_index = file_path.find('.view')
    start_index = end_index
    while file_path[start_index] != '/' and file_path[start_index] != '\\':
        start_index = start_index - 1
    return file_path[start_index + 1: end_index]


def get_button_id(line, after_word):
    result = ''
    i = line.find(after_word) + len(after_word)
    while line[i] != '"':
        result = result + line[i]
        i = i + 1
    return result


def get_tag(line, tag):
    result = ''
    i = line.find(tag) + len(tag)
    while line[i] != '<':
        result = result + line[i]
        i = i + 1
    return result


def get_form_data(file_path, result):
    form_id = get_form_id(file_path)
    form_t_short = ''
    form_description = ''
    file = open(file_path, 'r', encoding='utf-8')
    lines = file.readlines()
    for index, line in enumerate(lines, 0):
        if form_t_short != '' and form_description != '':
            break
        if re.search('<tshort>', line) is not None:
            form_t_short = get_tag(line, '<tshort>')
        if re.search('<description>', line) is not None:
            form_description = get_tag(line, '<description>')
    result.loc[result.size] = [form_id, form_t_short, form_description]
    file.close()
    return result


def get_buttons_data(file_path, result):
    form_id = get_form_id(file_path)
    file = open(file_path, 'r', encoding='utf-8')
    lines = file.readlines()
    button_lines = list()
    for index, line in enumerate(lines, 0):
        if re.search('<action id="', line) is not None or re.search('</action>', line) is not None:
            button_lines.append(index)
    for i in range(int(len(button_lines) / 2)):
        result.loc[result.size] = read_button(lines[button_lines[i * 2]:button_lines[i * 2 + 1]]) + [form_id]
    file.close()
    return result


# lines содержит строки от  <action> до </action>
def read_button(lines):
    button_id = ''
    button_name = ''
    button_title = ''
    button_description = ''
    button_transfer_type = ''
    button_transfer_address = ''
    for line in lines:
        if re.search('<action id="', line) is not None:
            button_id = get_button_id(line, 'action id="')
        elif re.search('<name>', line) is not None:
            button_name = get_tag(line, '<name>')
        elif re.search('<title>', line) is not None:
            button_title = get_tag(line, '<title>')
        elif re.search('<description>', line) is not None:
            button_description = get_tag(line, '<description>')
        elif re.search('<transferType>', line) is not None:
            button_transfer_type = get_tag(line, '<transferType>')
        elif re.search('<transfer>', line) is not None:
            button_transfer_address = get_tag(line, '<transfer>')
    return [button_id, button_name, button_title, button_description, button_transfer_type, button_transfer_address]
