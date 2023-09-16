import os
import time
import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

ranobeUrl = 'https://ranobehub.org/ranobe'
testOutput = "testOutput.html"
sourcePage = "sourcePage.html"
encoded = "encoded.html"
anotherEnc = "anotherEnc.html"

# Путь до текущего файла
file_dir = os.path.dirname(os.path.realpath('__file__'))
temp_data_dir = 'tempData/'


def writeInFile(file_name, mode, data):
    file_name = os.path.join(file_dir, temp_data_dir + file_name)
    file_name = os.path.abspath(os.path.realpath(file_name))
    with open(file_name, mode, encoding='utf-8') as file:
        file.write(data + "\n")
        file.close()


def getSourceHtlm(url):
    writeInFile(testOutput, "w", str(datetime.datetime.now()))
    driver = wd.Firefox()
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)
        pages = driver.find_elements(By.CLASS_NAME, "page-item")
        action = ActionChains(driver)
        action.click(pages[3]).perform()
        time.sleep(10)

        writeInFile(sourcePage, "w", driver.page_source)

    except Exception as ex:
        print(ex)
    finally:
        writeInFile(testOutput, "a+", str(datetime.datetime.now()))
        driver.close()
        driver.quit()


def main():
    getSourceHtlm(ranobeUrl)


if __name__ == '__main__':
    main()
