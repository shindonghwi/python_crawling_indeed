import glob
import json
import os
import time

import cloudscraper
from os import path

if __name__ == '__main__':
    folder_name_list = os.listdir(os.getcwd() + '/data/api_links')

    for company_name in folder_name_list:
        txt_list = glob.glob(os.getcwd() + '/data/api_links/{}/*.txt'.format(company_name))

        for txt_path in txt_list:
            country_name = txt_path.split('/')[-1].replace('.txt', '').replace('\n', '')
            print(company_name, country_name)
            txt_file = open(txt_path, 'r', encoding='utf-8')
            api_list = list(map(lambda s: s.strip(), txt_file.readlines()))
            txt_file.close()

            # 폴더 만들기
            new_folder_path = os.getcwd() + '/extract_data/{}'.format(company_name)
            try:
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
            except OSError:
                print("Error: Failed to create the directory.")

            json_file = open(new_folder_path + '/{}.txt'.format(country_name),'w', encoding='utf-8')

            for api in api_list:
                scraper = cloudscraper.create_scraper()
                req = scraper.get(api)
                json_str = req.content.decode('utf-8')
                json_data = json.loads(json_str)
                time.sleep(3)
                json_file.write(json_str)
                json_file.write('\n')
            json_file.close()
