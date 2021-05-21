from selenium import webdriver
from datetime import datetime


def worker_func(url):
    driver = webdriver.Chrome()
    driver.get(url=url)
    date = datetime.now()
    datef = datetime.strftime(date, "%d-%b-%Y-%H:%M")
    ss_name = f"{url.split('www.')[1]}-{datef}"
    driver.save_screenshot(f"./ss/{ss_name}.png")
    driver.close()


if __name__ == '__main__':
    worker_func('https://www.google.com')
