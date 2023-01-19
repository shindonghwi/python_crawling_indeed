import glob
import json
import os
import time

import cloudscraper
from os import path
from tqdm import tqdm
from os import path
import random

if __name__ == '__main__':
    folder_name_list = os.listdir(os.getcwd() + '/data/api_links')

    for company_name in tqdm(folder_name_list):
        txt_list = glob.glob(os.getcwd() + '/data/api_links/{}/*.txt'.format(company_name))
        for txt_path in txt_list:
            country_name = txt_path.split('/')[-1].replace('.txt', '').replace('\n', '')
            txt_file = open(txt_path, 'r', encoding='utf-8')
            api_list = list(map(lambda s: s.strip(), txt_file.readlines()))
            txt_file.close()
            print('start: ', company_name, country_name, ' // total: ', len(api_list))

            if len(api_list) != 0:
                # 회사 폴더 만들기
                new_folder_path = os.getcwd() + '/extract_data/{}'.format(company_name)
                try:
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                except OSError:
                    print("Error: Failed to create the directory.")

                api_result_file = new_folder_path + '/{}.txt'.format(country_name)
                if path.exists(api_result_file):
                    json_file = open(new_folder_path + '/{}.txt'.format(country_name), 'r+',
                                     encoding='utf-8')
                    success_index = len(json_file.readlines())
                else:
                    json_file = open(new_folder_path + '/{}.txt'.format(country_name), 'w+',
                                     encoding='utf-8')
                    success_index = 0

                for idx, api in enumerate(tqdm(api_list)):
                    if idx >= success_index:
                        scraper = cloudscraper.create_scraper()
                        req = scraper.get(api, headers={
                            'User-Agent': 'PostmanRuntime/7.30.0',
                            'Accept': '*/*',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Connection': 'keep-alive',
                            'Cookie': 'CTK=1gmiot58cisbu800; SHARED_INDEED_CSRF_TOKEN=BYTScsLYmqzB0ik5E0N7wZmnBFzEaC0S; __cf_bm=h_VFPbCdIxZMj7k0yU0VQ0z0vrgpgP91JrTeVIoImRI-1674105454-0-Af0+jyMabvJ0NGEW5wntBBScYqrwD3mizceZ11AvMRLHQ4+FXdjRfOPkOcH7eaSu0ZC8mIaYLoslqHa1KJzQJzU=; _cfuvid=xqpg9KdiMi9AMUV9RXBkcZtNyO4hK0cFGePgUkhKBPY-1674105454149-0-604800000; INDEED_CSRF_TOKEN=9c7QI5Ap236ZYDri8xycMeYsGRpHKPBO; LV="LA=1673519863:CV=1673519863:TS=1673519863"; indeed_rcc="LV:CTK"',
                        })

                        if req.status_code != 200:
                            exit()
                        json_str = req.content.decode('utf-8')
                        json_data = json.loads(json_str)
                        time.sleep(random.randrange(1,4))
                        json_file.write(json_str)
                        json_file.write('\n')

                json_file.close()
