import os
import time
import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement

ranobe_url = 'https://ranobehub.org/ranobe'
test_output = "testOutput.html"
source_page = "sourcePage.html"

# Путь до текущего файла
file_dir = os.path.dirname(os.path.realpath('__file__'))
temp_data_dir = 'tempData/'


def write_in_file(file_name: str, mode: str, data):
    file_name = os.path.join(file_dir, temp_data_dir + file_name)
    file_name = os.path.abspath(os.path.realpath(file_name))
    with open(file_name, mode, encoding='utf-8') as file:
        file.write(data + "\n")
        file.close()


def get_source_htlm(url: str):
    write_in_file(test_output, "w", str(datetime.datetime.now()))
    driver = wd.Firefox()
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)
        pages = driver.find_elements(By.CLASS_NAME, "page-item")
        # По сути тут надо цикл начать по pages, а лучше по другому параметру, но я пока не придумал
        # action = ActionChains(driver)
        # action.click(pages[3]).perform()
        # time.sleep(10)

        write_in_file(source_page, "w", driver.page_source)

        source_page_file = os.path.join(file_dir, temp_data_dir + source_page)
        source_page_file = os.path.abspath(os.path.realpath(source_page_file))
        write_in_file(test_output, "a+", source_page_file)

        with open(source_page_file, "r", encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            ranobe = soup.find_all('a', {'class': 'eight wide mobile five wide tablet four wide computer column'})
            for r in ranobe:
                write_in_file(test_output, "a+", str(r))

    except Exception as ex:
        print(ex)
    finally:
        write_in_file(test_output, "a+", str(datetime.datetime.now()))
        driver.close()
        driver.quit()


def main():
    source_page_file = os.path.join(file_dir, temp_data_dir + source_page)
    source_page_file = os.path.abspath(os.path.realpath(source_page_file))
    with open(source_page_file, "r", encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        ranobe = soup.find_all("div", class_="eight wide mobile five wide tablet four wide computer column")
        items: list[str] = []
        for r in ranobe:
            if r:
                items.append(str(r))

        print(str(len(items)))
    #get_source_htlm(ranobe_url)


if __name__ == '__main__':
    main()
