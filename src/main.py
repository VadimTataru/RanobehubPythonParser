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
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver, AbstractEventListener

from Novel import Novel


class EventListener(AbstractEventListener):
    print('Text!')


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
                print("Прокрутка завершена")
                break
            print("Появился новый контент, прокручиваем дальше")
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_single_ranobe_source_html(url: str, file_format: str = '.html'):
    options = wd.FirefoxOptions()
    # options.add_argument("-headless")
    driver = wd.Firefox(options)
    driver.set_window_size(1920, 1080)
    novel_id = re.search(r'(?<=ranobe/)\d+', url)
    event_firing_web_driver = EventFiringWebDriver(driver, EventListener())
    try:
        driver.get(url)
        time.sleep(3)
        expander_btn: Optional[WebElement]
        try:
            expander_btn = driver.find_element(By.CLASS_NAME, 'container-expander__button')
        except Exception:
            expander_btn = None

        if expander_btn is not None:
            ActionChains(driver).move_to_element(expander_btn).click().perform()

        volumes = driver.find_elements(By.CLASS_NAME, 'contents-volume')
        ActionChains(driver).scroll_by_amount(0, volumes[0].location['y']).perform()
        prev = ""
        for i, x in enumerate(volumes):
            chapter_selector = "#app-desktop-tabs > div > div.contents-volumes > " \
                               "div:nth-child({0}) > div.content.active > div:nth-child(1)".format(i+1)
            print("document.querySelector('{0}').scrollDown += 70".format(chapter_selector))
            ActionChains(driver).move_to_element(x).click().perform()
            time.sleep(2)
            while True:
                inner_html = x.get_attribute("innerHtml")
                with open("chapter_list.txt", "a", encoding="utf-8") as file:
                    file.write(x.get_attribute("innerHTML"))
                time.sleep(5)
                event_firing_web_driver.execute_script(
                    "document.querySelector('{0}').scrollTop += 1000".format(chapter_selector)
                )
                # TODO(Доработать условие выхода из цикла)
                if prev == inner_html:
                    break
                else:
                    prev = inner_html
            time.sleep(10)
        #     ranobe_file_name = novel_id[0] + '_' + str(i) + file_format
        #     write_in_file(ranobe_file_name, 'w', driver.page_source)
        #     chapters_file_name = 'chapters_' + ranobe_file_name
        #     with open(ranobe_file_name, 'r', encoding='utf-8') as file:
        #         soup = BeautifulSoup(file.read(), 'html.parser')
        #         chapters_div = soup.find_all('div', class_='contents-chapter contents-chapter_full')
        #         for x in chapters_div:
        #             print(x)
        #
        # print('Done!')
    except Exception as ex:
        print(ex.args)
        print(ex.__cause__)
        print(ex.__doc__)
        print(ex)
    finally:
        driver.close()
        driver.quit()


def main():

    url = 'https://ranobehub.org/ranobe/965-my-dungeon-life-rise-of-the-slave-harem'
    get_single_ranobe_source_html(url='https://ranobehub.org/ranobe/965-my-dungeon-life-rise-of-the-slave-harem')
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
