import io
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as Soup
import re
from datetime import datetime
from typing import IO
import math
import requests
from urllib import parse
import base64
import urllib
import os
import glob
from os import path


class Indeed:
    __file: IO[io.FileIO]

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.__driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        # self.__create_file()  # 회사 링크 리스트 만들기

        link_files = glob.glob(os.getcwd() + '/data/links/*.txt')

        for link_file_path in link_files:
            company_access_link_file = open(link_file_path, 'r', encoding='utf-8')  # 국가별 접속링크

            for idx, link in enumerate(company_access_link_file.readlines()):
                country_name = link \
                    .replace('https://', '') \
                    .split('.indeed.com/cmp')[0] \
                    .replace('\n', '')

                company_name = parse.unquote(
                    link.replace('https://{}.indeed.com/cmp/'
                                 .format(country_name), '').replace('/jobs', '')
                ).replace('\n', '')

                access_path = link.replace("\n", "")

                self.__move_company_page(access_path, country_name, company_name)
            company_access_link_file.close()

    def __create_file(self):
        """ 회사 링크리스트 만들기 """

        # 나라 리스트
        country_file = open(os.getcwd() + '/data/country_list', 'r', encoding='utf-8')
        country_list = []
        for idx, country in enumerate(country_file.readlines()):
            country_list.append(country.replace("\n", ""))
        country_file.close()

        # 회사 리스트
        company_file = open(os.getcwd() + '/data/company_list', 'r', encoding='utf-8')
        company_list = []
        for idx, company in enumerate(company_file.readlines()):
            company_list.append(company.replace("\n", ""))
        company_file.close()

        # 링크리스트
        for company in company_list:
            link_file = open(os.getcwd() + '/data/links/{}.txt'.format(
                company), 'w', encoding='utf-8')

            for country in country_list:
                link_file.write('https://{}.indeed.com/cmp/{}/jobs'.format(
                    country, urllib.parse.quote(company))
                )
                link_file.write('\n')
            link_file.close()

    def __scroll_down(self, count):
        # 스크롤 높이 가져옴
        last_height = self.__driver.execute_script("return document.body.scrollHeight")

        for i in range(0, count):
            # 끝까지 스크롤 다운
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 1초 대기
            time.sleep(0.5)

            # 스크롤 다운 후 스크롤 높이 다시 가져옴
            new_height = self.__driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def __move_company_page(self, link, country_name, company_name):
        print('start -> ', country_name, company_name, link)

        try:
            if not os.path.exists(os.getcwd() + '/data/api_links/{}'.format(company_name)):
                os.makedirs(os.getcwd() + '/data/api_links/{}'.format(company_name))
        except OSError:
            print("Error: Failed to create the directory.")

        if path.exists(
                os.getcwd() + '/data/api_links/{}/{}.txt'.format(company_name, country_name)):
            return

        print('run -> ', country_name, company_name, link)
        time.sleep(2.5)
        self.__driver.get(link)
        html = self.__get_current_html()

        menu_list_html = html.find('div', 'css-1nkr1un eu4oa1w0') \
            .find_all('li', attrs={'data-tn-element': True})

        total_count = 0

        for menu in menu_list_html:
            if 'jobs-tab' in menu['data-tn-element']:
                if menu.find('div', 'css-r228jg eu4oa1w0'):
                    total_count = menu.find('div', 'css-r228jg eu4oa1w0').text
        total_count = self.__regex_number(str(total_count))
        total_job_page_rest = int(total_count) % 150

        if total_job_page_rest == 0:
            total_job_page = int(int(total_count) / 150)
        else:
            total_job_page = int(math.floor(int(total_count) / 150) + 1)

        company_api_key_code_list = []
        for page in range(0, total_job_page):
            if page >= 1:
                current_url = self.__driver.current_url.split('?start')[0]
                next_page_url = "{}?start={}".format(current_url, str(page * 150))
                self.__driver.get(next_page_url)
            time.sleep(4)
            self.__get_company_key(company_api_key_code_list)

        api_result_file = os.getcwd() + '/data/api_links/{}/{}.txt'.format(
            company_name, country_name)

        if path.exists(api_result_file):
            api_link_file = open(api_result_file, 'r+', encoding='utf-8')
            success_index = len(api_link_file.readlines())
        else:
            api_link_file = open(api_result_file, 'w+', encoding='utf-8')
            success_index = 0

        for idx, key in enumerate(company_api_key_code_list):
            if idx >= success_index:
                api_url = 'https://www.indeed.com/viewjob' \
                          '?viewtype=embedded' \
                          '&jk={}' \
                          '&from=vjs' \
                          '&tk=1gmvgpksbh0kh800' \
                          '&continueUrl=%2Fjobs%3Fsc%3D0fcckey%253Ad1342c7b78af94a6%252Ckf%253Afcckey%2528d1342c7b78af94a6%2529%252Cq%253A%253B%26q%3Dplug%2Bpower%26vjk%3Da2e4eb960ae9084f' \
                          '&spa=1' \
                          '&hidecmpheader=1'.format(key)
                api_link_file.write(api_url)
                api_link_file.write('\n')
        api_link_file.close()

    def __get_company_key(self, company_api_key_code_list):
        c_html = self.__get_current_html()
        if c_html.find('div', 'css-6a3erz eu4oa1w0'):
            ul_html = c_html.find('div', 'css-6a3erz eu4oa1w0') \
                .find('ul', attrs={'data-testid': True}) \
                .find_all('li', attrs={'data-tn-entityid': True})

            for i in ul_html:
                key = str(i['data-tn-entityid']).split(',')[1]
                company_api_key_code_list.append(key)

    def __find_xpath(self, xpath: str, err_msg: str):
        try:
            WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            ).click()
            time.sleep(0.2)
        except Exception as e:
            print(err_msg, e)
            self.__driver.quit()

    def __find_xpath_text(self, xpath: str, err_msg: str):
        try:
            text = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            ).text
            return text
        except Exception as e:
            print(err_msg, e)
            self.__driver.quit()

    def __regex_number(self, msg: str):
        """ 숫자만 추출하는 정규식 """
        return re.sub(r'[^0-9]', '', msg)

    def __get_current_html(self):
        """ 현재 페이지의 Html 코드를 가져오기 """
        return Soup(self.__driver.page_source, "lxml")

    def __extract_page_info(self, html):
        """ 페이지 정보 추출 """
        total_people_count_text = html \
            .find('div', 'search-results-container') \
            .find('div').text
        total_people_count = self.__regex_number(total_people_count_text)
        total_people_page_rest = int(total_people_count) % 10
        total_people_page = int(total_people_count) / 10
        if total_people_page_rest != 0:
            total_people_page += 1
        if total_people_page >= 100:
            total_people_page = 100
        total_people_page = math.ceil(total_people_page)
        return total_people_page


if __name__ == '__main__':
    Indeed()
