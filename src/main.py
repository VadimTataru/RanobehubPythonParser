import time
import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

ranobeUrl = 'https://ranobehub.org/ranobe'
testOutput = "test/testOutput.html"
sourcePage = "test/sourcePage.html"


def writeInFile(filename, mode, data):
    with open(filename, mode, encoding='utf-8') as file:
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
        with open("test/page-items.html", "w") as file:
            for page in pages:
                file.write(str(page.tag_name) + "\n")

            file.close()

        action = ActionChains(driver)
        action.click(pages[3]).perform()
        time.sleep(10)
        writeInFile(sourcePage, "a+", driver.page_source)
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
