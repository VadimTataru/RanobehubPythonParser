import json
import os
import re
import time
from typing import Optional

from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from Novel import Novel
from src.NovelChapter import NovelChapter

ranobe_url = 'https://ranobehub.org/ranobe'
source_page_file_name = "sourcePage.html"
novel_list_file_name = "novel_list.txt"

# Путь до текущего файла
file_dir = os.path.dirname(os.path.realpath('__file__'))
temp_data_dir = 'tempData/'


def write_in_file(file_name: str, mode: str, data):
    file_name = os.path.join(file_dir, temp_data_dir + file_name)
    file_name = os.path.abspath(os.path.realpath(file_name))
    with open(file_name, mode, encoding='utf-8') as file:
        file.write(data + "\n")
        file.close()


def get_source_html(url):
    options = wd.FirefoxOptions()
    options.add_argument("-headless")
    driver = wd.Firefox(options)
    driver.set_window_size(1920, 1080)
    try:
        driver.get(ranobe_url)
        time.sleep(3)
        button_load_more = driver.find_element(By.CLASS_NAME, 'text')
        ActionChains(driver).move_to_element(button_load_more).click().perform()
        while True:
            last_height = driver.execute_script("return document.body.scrollHeight")
            # Прокрутка вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Пауза, пока загрузится страница.
            time.sleep(2)
            # Вычисляем новую высоту прокрутки и сравниваем с последней высотой прокрутки.
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                write_in_file(source_page_file_name, "w", driver.page_source)
                source_page_file = os.path.join(file_dir, temp_data_dir + source_page_file_name)
                os.path.abspath(os.path.realpath(source_page_file))
                print("Прокрутка завершена.")
                break
            print("Появился новый контент, прокручиваем дальше.")
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_first_chapter_link_with_selenium(novel_url: str):
    """ Поиск ссылки на первую главу новеллы. Работает с ознакомительной страницы.
    \n Note: Запускается WebDriver Firefox без опции -headless! \n
    Arguments:
    \n novel_url: Ссылка на новеллу.\n
    Returns:
    \n returns: Ссылка на первую главу новеллы.\n"""

    driver = wd.Firefox()
    driver.set_window_size(1920, 1080)
    try:
        driver.get(novel_url)
        time.sleep(3)
        expander_btn: Optional[WebElement]
        try:
            expander_btn = driver.find_element(By.CLASS_NAME, 'container-expander__button')
        except Exception:
            expander_btn = None

        if expander_btn is not None:
            ActionChains(driver).move_to_element(expander_btn).click().perform()

        first_vol = driver.find_element(By.CLASS_NAME, 'contents-volume')
        ActionChains(driver).scroll_by_amount(0, first_vol.location['y']).perform()
        ActionChains(driver).move_to_element(first_vol).click().perform()
        time.sleep(2)
        return str(first_vol \
                   .find_element(By.CSS_SELECTOR,
                                 '#app-desktop-tabs > div > div.contents-volumes > div:nth-child(1) > '
                                 'div.content.active > div:nth-child(1) > div:nth-child(1) > '
                                 'div:nth-child(1) > div > a').get_property('href'))
    except Exception as ex:
        print(ex.args)
        print(ex.__cause__)
        print(ex.__doc__)
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_first_chapter_link(url: str):
    """Преобразование ссылки новелы в ссылку на её первую главу.

    :param url: Ссылка на новелу.
    :return: Ссылка на первую главу новелы по шаблону.
    """
    match = re.match(r'(https://ranobehub.org/ranobe/\d+)', url)
    if match:
        chapter_url = match.group(1)
        return chapter_url + '/1/1'
    else:
        return ''


def get_novel_chapter(chapter_link: str, driver: WebDriver):
    """Парсинг главы новеллы.
    \n Note: В WebDriver следует включать опцию -headless! \n

    :param chapter_link: Ссылка на страницу чтения главы новеллы.
    :param driver: WebDriver.
    :return: NovelChapter.
    """

    novel_id = int(re.search(r'(\w+?<=ranobe/)\d+', chapter_link).group())
    try:
        driver.get(chapter_link)
        time.sleep(2)
        main_container = driver.find_element(By.CLASS_NAME, 'container_main')
        title_div_web_elem = main_container.find_element(By.CLASS_NAME, 'title-wrapper')
        # Элементы с нужной информацией
        volume_web_elem = main_container.find_element(By.XPATH, '/html/body/div[2]/div[4]/ol/li[3]/a/span')
        title_web_elem = title_div_web_elem.find_element(By.TAG_NAME, 'h1')
        paragraph_web_elems = title_div_web_elem.find_element(By.XPATH, './..').find_elements(By.TAG_NAME, 'p')
        button_web_elems = driver.find_elements(By.CLASS_NAME, 'read_nav__buttons__manage')

        next_chapter_link = ""
        text_content = ""
        for item in paragraph_web_elems:
            text_content += item.text + "\n"

        for item in button_web_elems:
            if item.get_attribute('data-hotKey') == 'right':
                next_chapter_link = item.get_attribute('href')

        return NovelChapter(
            title_rus=title_web_elem.text,
            source_link=chapter_link,
            next_source_link=next_chapter_link,
            content=text_content,
            volume=volume_web_elem.text,
            novel_id=novel_id
        )
    except Exception as ex:
        print(ex.args)
        print(ex.__cause__)
        print(ex.__doc__)
        print(ex)


def get_all_next_chapters(chapter_link: str, driver: WebDriver, should_write: bool = False,
                          file_name: str = "chapters.txt"):
    """ Парсинг всех глав, начиная с chapter_link.
        \n Note: В WebDriver следует включать опцию -headless! \n
        Arguments:
        \n chapter_link: Ссылка на новеллу.\n
        \n driver: WebDriver.\n
        \n should_write: Записывать в файл сразу или просто вернуть массив данных.\n
        \n file_name: Имя файла для записи.\n
        Returns:
        \n returns: Массив глав новеллы.\n """

    url = chapter_link
    novel_chapters: list[NovelChapter] = []
    process_index = 0
    try:
        while True:
            print(str(process_index) + " step is done.")

            chapter = get_novel_chapter(url, driver)
            if should_write:
                write_as_json(chapter, file_name)
            novel_chapters.append(chapter)

            print(str(process_index) + " step is done.")
            process_index += 1

            if chapter.next_source_link == "":
                return novel_chapters
            else:
                url = chapter.next_source_link
    except Exception as ex:
        print(ex.args)
        print(ex.__cause__)
        print(ex.__doc__)
        print(ex)
    finally:
        driver.close()
        driver.quit()


def write_list_as_json(data: [], file_name: str):
    """ Запись массива данных в файл в формате json.
        Arguments:
        \n data: Массив данных на запись.\n
        \n file_name: Имя файла.\n """

    with open(file_name, "w+", encoding='utf-8') as file:
        file.write('[' + '\n')
        for item in data:
            file.write(json.dumps(item.__dict__, indent=4, ensure_ascii=False))
            file.write(', \n')
        file.write(']')


def write_as_json(data, file_name: str):
    """ Запись объекта данных в файл в формате json.
            Arguments:
            \n data: Объект данных на запись.\n
            \n file_name: Имя файла.\n """
    with open(file_name, "a+", encoding='utf-8') as file:
        file.write(json.dumps(data.__dict__, indent=4, ensure_ascii=False))
        file.write(',\n')


def main():
    url = 'https://ranobehub.org/ranobe/965-my-dungeon-life-rise-of-the-slave-harem'
    value = get_first_chapter_link(url)
    print(value)
    # first_chapter_link = get_first_chapter_link(
    #     novel_url='https://ranobehub.org/ranobe/965-my-dungeon-life-rise-of-the-slave-harem'
    # )
    # options = wd.ChromeOptions()
    # options.add_argument("-headless")
    # driver = wd.Chrome(options)
    # driver.set_window_size(1920, 1080)
    # url2 = 'https://ranobehub.org/ranobe/965/1/1'
    # chapters = get_all_next_chapters(url2, driver, True, 'chapters.txt')
    # print(len(chapters))
    # write_list_as_json(chapters, 'chapters.txt')
    # get_source_html(ranobe_url)
    # source_page_file = os.path.join(file_dir, temp_data_dir + source_page_file_name)
    # source_page_file = os.path.abspath(os.path.realpath(source_page_file))
    # novel_list_file = os.path.join(file_dir, temp_data_dir + novel_list_file_name)
    # novel_list_file = os.path.abspath(os.path.realpath(novel_list_file))
    # with open(source_page_file, "r", encoding='utf-8') as file:
    #     soup = BeautifulSoup(file.read(), 'html.parser')
    #     ranobe_div = soup.find_all("div", class_="eight wide mobile five wide tablet four wide computer column")
    #     novel_list: list[Novel] = []
    #     for ranobe in ranobe_div:
    #         if ranobe:
    #             novel_list.append(Novel(title_rus=ranobe.find('div', class_='header').find('h4').find('a').text.strip(),
    #                                     title_en=ranobe.find('div', class_='header').find('h5').find('a').text.strip(),
    #                                     source_link=ranobe.find('a', class_='image')['href'],
    #                                     img_link=ranobe.find('img', class_='poster_grid')['data-src']))
    # print(len(ranobe_div))
    # with open(novel_list_file, "w+", encoding='utf-8') as file:
    #     file.write('[' + '\n')
    #     for novel in novel_list:
    #         file.write(json.dumps(novel.__dict__, indent=4, ensure_ascii=False))
    #         file.write(', \n')
    #     file.write(']')


if __name__ == '__main__':
    main()
