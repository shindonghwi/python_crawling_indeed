import glob
import os

if __name__ == '__main__':
    folder_list = glob.glob(os.getcwd() + '/data/api_links/*')

    counting = 0

    for folder_path in folder_list:
        txt_file_list = glob.glob(folder_path + '/*.txt')

        for txt_file_path in txt_file_list:

            f = open(txt_file_path, 'r', encoding='utf-8')

            counting = counting + len(f.readlines())

    print(counting)
    #
