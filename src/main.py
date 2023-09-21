import json
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from Novel import Novel

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


def main():
    #get_source_html(ranobe_url)
    source_page_file = os.path.join(file_dir, temp_data_dir + source_page_file_name)
    source_page_file = os.path.abspath(os.path.realpath(source_page_file))
    novel_list_file = os.path.join(file_dir, temp_data_dir + novel_list_file_name)
    novel_list_file = os.path.abspath(os.path.realpath(novel_list_file))
    with open(source_page_file, "r", encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        ranobe_div = soup.find_all("div", class_="eight wide mobile five wide tablet four wide computer column")
        novel_list: list[Novel] = []
        for ranobe in ranobe_div:
            if ranobe:
                novel_list.append(Novel(title_rus=ranobe.find('div', class_='header').find('h4').find('a').text.strip(),
                                        title_en=ranobe.find('div', class_='header').find('h5').find('a').text.strip(),
                                        source_link=ranobe.find('a', class_='image')['href'],
                                        img_link=ranobe.find('img', class_='poster_grid')['data-src']))
    print(len(ranobe_div))
    with open(novel_list_file, "w+", encoding='utf-8') as file:
        file.write('[' + '\n')
        for novel in novel_list:
            file.write(json.dumps(novel.__dict__, indent=4, ensure_ascii=False))
            file.write(', \n')
        file.write(']')


if __name__ == '__main__':
    main()
