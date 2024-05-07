from bs4 import BeautifulSoup
import json
import asyncio
from pyppeteer import launch
import os
import time

# Читаем файл html и возвращаем обработтанные с помощью BeautifulSoup данные
def parse_html_content_with_soup(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        # Чтение содержимого файла HTML
        html_content = file.read()

        # Парсинг HTML с помощью BeautifulSoup
        html_content_soup = BeautifulSoup(html_content, 'html.parser')
                
        return html_content_soup

# Ищем в html_content_soup блоки с заданным классом и возвращаем первый
# Т.к. используем select то можно использовать несколько классов class_name='.class1 .class2'
def extract_first_element_by_class(html_content_soup, class_name):
    # Проверяем, что html_content_soup не равен None
    if html_content_soup is None:
        return None

    # Находим все элементы с указанным классом внутри найденного элемента
    found_elements = html_content_soup.select(class_name)
    
    # Если элементы найдены, возвращаем самый первый
    if found_elements:
        return found_elements[0]
    else:
        return None

# Ищем в html_content_soup блоки с заданным классом и возвращаем их
# Т.к. используем select то можно использовать несколько классов class_name='.class1 .class2'
def extract_elements_by_class(html_content_soup, class_name):
    # Проверяем, что html_content_soup не равен None
    if html_content_soup is None:
        return None

    # Находим все элементы с указанным классом внутри найденного элемента
    #found_elements = html_content_soup.find_all(class_=class_name)
    found_elements = html_content_soup.select(class_name)
    
    # Если элементы найдены, возвращаем их
    if found_elements:
        return found_elements
    else:
        return None

# Ищем в html_content_soup блок с заданным id и возвращаем его
def extract_element_by_id(html_content_soup, element_id):
    # Проверяем, что html_content_soup не равен None
    if html_content_soup is None:
        return None

    # Находим все элементы с указанным классом внутри найденного элемента
    found_element = html_content_soup.find(id=element_id)
    
    # Если элементы найдены, возвращаем их
    if found_element:
        return found_element
    else:
        return None

# Парсим раздел смыслов на странице oxfordlearnersdictionaries.com (корректно только для 'verb' с senses_multiple и 'adjective') и возвращаем в виде словаря 
def get_senses_dict(html_content_soup):
    result = []
    # Перебираем найденные блоки - под одним заголовком/значением внутри блока может быть один и более смыслов с примерами
    for shcut_g_blok in html_content_soup:
        shcut_block = extract_first_element_by_class(shcut_g_blok, '.shcut')
        shcut_sense = ''
        if shcut_block:
            shcut_sense = shcut_block.text 
        sense_blocks = extract_elements_by_class(shcut_g_blok, '.sense')
        if sense_blocks:
            for sense_block in sense_blocks:
                my_dict = dict()
                my_dict['sense'] = shcut_sense
                sensenum_value = sense_block.get('sensenum')
                if sensenum_value:
                    my_dict['sensenum'] = sensenum_value
                    cefr_value = sense_block.get('cefr')
                    if cefr_value:
                        my_dict['level'] = cefr_value
                grammar_block = extract_first_element_by_class(sense_block, '.grammar')
                if grammar_block:                                    
                    my_dict['grammar'] = [el.strip() for el in grammar_block.text[1:-1].split(',')]
                labels_block = extract_first_element_by_class(sense_block, '.labels')
                if labels_block:
                    my_dict['labels'] = [el.strip() for el in labels_block.text[1:-1].split(',')]
                definition_block = extract_first_element_by_class(sense_block, '.def')
                if definition_block:
                    my_dict['definition'] = definition_block.text
                examples_block = extract_first_element_by_class(sense_block, '.examples')
                if examples_block:
                    my_dict['examples'] = []
                    li_tag_blocks = examples_block.find_all('li')
                    if li_tag_blocks:
                        for li_tag_block in li_tag_blocks:
                            cf_block = extract_first_element_by_class(li_tag_block, '.cf')
                            example = dict()
                            if cf_block:
                                example['explanation'] = cf_block.text
                            x_block = extract_first_element_by_class(li_tag_block, '.x')
                            if x_block:
                                example['example'] = x_block.text
                            example_label_block = extract_first_element_by_class(li_tag_block, '.labels')
                            if example_label_block:
                                example['label'] = example_label_block.text[1:-1]
                            my_dict['examples'].append(example)
                result.append(my_dict)                    
    return result

# Парсим раздел смыслов на странице oxfordlearnersdictionaries.com (корректно только для 'noun') и возвращаем в виде словаря 
def get_senses_noun_dict(html_content_soup):
    result = []
    for sense_block in html_content_soup:
        my_dict = dict()
        sensenum_value = sense_block.get('sensenum')
        if sensenum_value:
            my_dict['sensenum'] = sensenum_value
            cefr_value = sense_block.get('cefr')
            if cefr_value:
                my_dict['level'] = cefr_value
        grammar_block = extract_first_element_by_class(sense_block, '.grammar')
        if grammar_block:
            my_dict['grammar'] = [el.strip() for el in grammar_block.text[1:-1].split(',')]
        labels_block = extract_first_element_by_class(sense_block, '.labels')
        if labels_block:
            my_dict['labels'] = [el.strip() for el in labels_block.text[1:-1].split(',')]
        definition_block = extract_first_element_by_class(sense_block, '.def')
        if definition_block:
            my_dict['definition'] = definition_block.text
        examples_block = extract_first_element_by_class(sense_block, '.examples')
        if examples_block:
            my_dict['examples'] = []
            li_tag_blocks = examples_block.find_all('li')
            if li_tag_blocks:
                for li_tag_block in li_tag_blocks:
                    cf_block = extract_first_element_by_class(li_tag_block, '.cf')
                    example = dict()
                    if cf_block:
                        example['explanation'] = cf_block.text
                    x_block = extract_first_element_by_class(li_tag_block, '.x')
                    if x_block:
                        example['example'] = x_block.text
                    example_label_block = extract_first_element_by_class(li_tag_block, '.labels')
                    if example_label_block:
                        example['label'] = example_label_block.text[1:-1]
                    my_dict['examples'].append(example)
        result.append(my_dict)
    return result

# Парсим раздел смыслов на странице oxfordlearnersdictionaries.com (корректно только для 'verb' c sense_single) и возвращаем в виде словаря 
def get_senses_verb_dict(html_content_soup):
    result = []
    for sense_block in html_content_soup:
        my_dict = dict()
        grammar_block = extract_first_element_by_class(sense_block, '.grammar')
        if grammar_block:
            my_dict['grammar'] = [el.strip() for el in grammar_block.text[1:-1].split(',')]
        labels_block = extract_first_element_by_class(sense_block, '.sensetop .labels')
        if labels_block:
            my_dict['labels'] = [el.strip() for el in labels_block.text[1:-1].split(',')]
        sense_cf_block = extract_first_element_by_class(sense_block, '.cf')
        if sense_cf_block:
            my_dict['explanation'] = sense_cf_block.text
        definition_block = extract_first_element_by_class(sense_block, '.def')
        if definition_block:
            my_dict['definition'] = definition_block.text
        examples_block = extract_first_element_by_class(sense_block, '.examples')
        if examples_block:
            my_dict['examples'] = []
            li_tag_blocks = examples_block.find_all('li')
            if li_tag_blocks:
                for li_tag_block in li_tag_blocks:
                    cf_block = extract_first_element_by_class(li_tag_block, '.cf')
                    example = dict()
                    if cf_block:
                        example['explanation'] = cf_block.text
                    x_block = extract_first_element_by_class(li_tag_block, '.x')
                    if x_block:
                        example['example'] = x_block.text
                    example_label_block = extract_first_element_by_class(li_tag_block, '.labels')
                    if example_label_block:
                        example['label'] = example_label_block.text[1:-1]
                    my_dict['examples'].append(example)
        result.append(my_dict)
    return result

# Парсим раздел идиом на странице oxfordlearnersdictionaries.com (корректно только для 'verb', 'adjective' и 'noun') и возвращаем в виде словаря 
def get_idioms_dict(html_content_soup):
    result = []
    for idm_g_blok in html_content_soup:
        idm_block = extract_first_element_by_class(idm_g_blok, '.webtop .idm')
        idm = ''
        if idm_block:
            idm = idm_block.text
            idiom_sense_blocks = extract_elements_by_class(idm_g_blok, '.sense')
            if idiom_sense_blocks:
                for idiom_sense_block in idiom_sense_blocks:
                    idiom_dict = dict()
                    idiom_dict['text'] = idm
                    idiom_definition_block = extract_first_element_by_class(idiom_sense_block, '.def')
                    if idiom_definition_block:
                        idiom_dict['definition'] = idiom_definition_block.text
                    idiom_label_block = extract_first_element_by_class(idiom_sense_block, '.sensetop .labels')
                    if idiom_label_block:
                        idiom_dict['label'] = [el.strip() for el in idiom_label_block.text[1:-1].split(',')]
                    idiom_examples_block = extract_first_element_by_class(idiom_sense_block, '.examples')
                    if idiom_examples_block:
                        idiom_x_blocks = extract_elements_by_class(idiom_examples_block, '.x')
                        if idiom_x_blocks:
                            idiom_examples = []
                            for idiom_x_block in idiom_x_blocks:
                                idiom_examples.append(idiom_x_block.text)
                            idiom_dict['examples'] = idiom_examples
                    result.append(idiom_dict)
    return result

def get_json_from_html(html_content_soup):    
    data = dict()
    element_id = 'entryContent'
    found_element = extract_element_by_id(html_content_soup, element_id)
    if found_element:
        # Проверяем на странице искомое слово
        headword_block = extract_first_element_by_class(found_element, '.webtop .headword')
        keyword = ''
        if headword_block:
            keyword = headword_block.text
            print('!!!parse_word!!! ', keyword)
            data[keyword] = dict()
            # Находим часть речи
            pos_block = extract_first_element_by_class(found_element, '.webtop .pos')
            part_of_speech = ''
            if pos_block:
                part_of_speech = pos_block.text
                data[keyword]["part_of_speech"] = part_of_speech
            # Находим уровень слова - задается двумя последними символами класса <span> внутри блока
            symbols_block = extract_first_element_by_class(found_element, '.webtop .symbols')
            if symbols_block:
                # Находим элемент <span>
                span_element = symbols_block.find('span')
                if span_element:
                    # Извлекаем имя класса элемента <span>
                    class_name = span_element['class'][0]
                    data[keyword]["level"] = class_name[-2:]
            
            shcut_g_bloks = extract_elements_by_class(found_element, '.senses_multiple .shcut-g')
            if shcut_g_bloks:
                    data[keyword]["senses"] = get_senses_dict(shcut_g_bloks)
            else:
                sense_bloks = extract_elements_by_class(found_element, '.senses_multiple .sense')
                if sense_bloks:
                    data[keyword]["senses"] = get_senses_noun_dict(sense_bloks)
                else:
                    sense_bloks = extract_elements_by_class(found_element, '.sense_single .sense')
                    if sense_bloks:
                        data[keyword]["senses"] = get_senses_verb_dict(sense_bloks)
            
            idm_g_bloks = extract_elements_by_class(found_element, '.idioms .idm-g')
            if idm_g_bloks:
                data[keyword]["idioms"] = get_idioms_dict(idm_g_bloks)

    else:
        print(f"Элемент с ID '{element_id}' не найден в HTML файле.")
    result = json.dumps(data, ensure_ascii=False, indent=4)
    return result

def save_file(data, file_name, file_path=None):
    if file_path is None:
        file_path = file_name  # Если не указан путь, используем текущую директорию
    else:
        file_path = os.path.join(file_path, file_name)  # Если указан путь, добавляем к нему имя файла
        
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)  # Записываем данные в файл
        print(f"Файл '{file_name}' успешно сохранен.")
    except Exception as e:
        print(f"Ошибка при сохранении файла '{file_name}': {e}")

async def search_html_page(word_info):
    word = word_info.get('word')
    if word == None:
        return None
    # Запуск браузера
    browser = await launch(executablePath='c:\\Program Files\\chrome-win\\chrome.exe', userDataDir ='d:\\!projects\\MyPythonProjects\\oxford_parser\\user\\', headless=False)

    # Создание новой вкладки
    page = await browser.newPage()

    # Переход на веб-страницу
    await page.goto(r'https://www.oxfordlearnersdictionaries.com/')

    # Выделяем строку поиска
    search_input = await page.querySelector('input.searchfield_input')

    # Ввод текста для поиска
    await search_input.type(word)

    # Нажатие клавиши Enter для выполнения поиска
    await search_input.press('Enter')

    # Ожидание загрузки результатов поиска
    await page.waitForNavigation()

    # Получение html контента
    html_content = await page.content()
   
    # Парсинг HTML с помощью BeautifulSoup
    html_content_soup = BeautifulSoup(html_content, 'html.parser')

    # Парсинг HTML и преобразование данных в JSON
    result = get_json_from_html(html_content_soup)

    # Закрытие браузера
    await browser.close()

    return result

async def search_word_on_page(word_info, page):
    word = word_info.get('word')
    if word == None:
        return None

     # Выделяем строку поиска
    search_input = await page.querySelector('input.searchfield_input')

    # Ввод текста для поиска
    await search_input.type(word)

    # Нажатие клавиши Enter для выполнения поиска
    await search_input.press('Enter')

    # Ожидание загрузки результатов поиска
    await page.waitForNavigation(timeout=10000)

    # Получение html контента
    html_content = await page.content()

    # Парсинг HTML с помощью BeautifulSoup
    html_content_soup = BeautifulSoup(html_content, 'html.parser')

    return html_content_soup

def check_part_of_speech(html_content_soup, word_info):
    result = False
    element_id = 'entryContent'
    found_element = extract_element_by_id(html_content_soup, element_id)
    if found_element:
        # Проверяем на странице искомое слово
        headword_block = extract_first_element_by_class(found_element, '.webtop .headword')
        keyword = ''
        if headword_block:
            keyword = headword_block.text
            if keyword == word_info.get('word'):
                # Находим часть речи
                pos_block = extract_first_element_by_class(found_element, '.webtop .pos')
                part_of_speech = ''
                if pos_block:
                    part_of_speech = pos_block.text
                    pos = word_info.get('pos')
                    if pos:
                        if part_of_speech == pos:
                            result = True
                    else:
                        if part_of_speech == '':
                            result = True
    return result

def get_correct_link(html_content_soup, word_info):
    result = None
    element_id = 'relatedentries'
    found_element = extract_element_by_id(html_content_soup, element_id)
    if found_element:
        li_blocks = found_element.find_all('li')
        if li_blocks:
            for li_block in li_blocks:
                pos_block = li_block.find('pos')
                # Проверяем чтобы либо часть речи на странице была такой, как мы задаем в word_info['pos']                
                if (pos_block and pos_block.text == word_info.get('pos')):
                    span_block = li_block.find('span')
                    if span_block:
                        children = span_block.contents
                        # Извлекаем текст только до элемента <pos-g>
                        text = ''
                        for child in children:
                            if child.name == 'pos-g':  # Проверяем, является ли текущий элемент <pos-g>
                                break
                            text += str(child)  # Добавляем текст текущего элемента в строку

                        if text.strip() == word_info.get('word'):
                            a_blosk = li_block.find('a')
                            if a_blosk:
                                href_value = a_blosk['href']
                            return href_value
                else:
                    continue
    return result

async def search_html_pages(words_info):
    # Запуск браузера
    browser = await launch(executablePath='c:\\Program Files\\chrome-win\\chrome.exe', userDataDir ='d:\\!projects\\MyPythonProjects\\oxford_parser\\user\\', headless=False)

    # Создание новой вкладки
    page = await browser.newPage()

    # Переход на веб-страницу
    await page.goto(r'https://www.oxfordlearnersdictionaries.com/')

    results = {}  # Словарь для хранения результатов поиска
    
    for word_info in words_info:
        # Ищем на сайте страницу со словом (пока мы не знаем какая эта часть речи)
        html_content_soup = await search_word_on_page(word_info, page)

        # Проверяем часть речи на найденной странице
        if check_part_of_speech(html_content_soup, word_info):
            # Парсинг HTML и преобразование данных в JSON
            result = get_json_from_html(html_content_soup)
            results[word_info['word']] = result  # Сохраняем результат поиска в словаре
        else:
            link = get_correct_link(html_content_soup, word_info)
            if link:
                # Переход на веб-страницу
                await page.goto(link)

                # Получение html контента
                html_content = await page.content()

                # Парсинг HTML с помощью BeautifulSoup
                html_content_soup_new = BeautifulSoup(html_content, 'html.parser')

                result = get_json_from_html(html_content_soup_new)
                results[word_info['word']] = result  # Сохраняем результат поиска в словаре

    # Закрытие браузера
    await browser.close()

    # Сохранение результатов поиска в файлы
    for word, result in results.items():
        save_file(result, word)

#words = ['resuscitate', 'fairness', 'buck', 'spontaneously', 'cool', 'through', 'take']
words_info = [
    {'word': 'resuscitate', 'pos': 'verb'},
    {'word': 'fairness', 'pos': 'noun'},
    {'word': 'buck', 'pos': 'noun'},
    {'word': 'spontaneously', 'pos': 'adverb'},
    {'word': 'cool', 'pos': 'adjective'},
    {'word': 'through', 'pos': 'preposition'},
    {'word': 'take', 'pos': 'verb'}
]

words_info1 = [
    {'word': 'take', 'pos': 'noun'}
    
]
#print(os.path.dirname(__file__))
asyncio.get_event_loop().run_until_complete(search_html_pages(words_info))

#word = 'resuscitate'
#word = 'cool'
#word_info = {'word' : 'take', 'pos' : 'verb'}
#search_word(word)