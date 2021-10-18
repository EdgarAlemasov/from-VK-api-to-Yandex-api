import json

import requests
from pprint import pprint
import time
from tqdm import tqdm

photo = {}


# ПОЛУЧЕНИЕ ФОТО ИЗ ВК И СОХРАНЕНИЕ ИХ В СЛОВАРЬ
class VkUser():

    def id_user():
        url = 'https://api.vk.com/method/users.get'
        token = ''
        params = {'access_token': token, 'v': '5.131'}
        response = requests.get(url=url, params=params)
        pprint(response.json())

    def get_user_photo():
        url = 'https://api.vk.com/method/photos.get'
        token = ''
        params = {'owner_id': 17181069, 'album_id': 'profile', 'photo_sizes': 1, 'access_token': token, 'v': '5.131',
                  'extended': 1}
        response = requests.get(url=url, params=params)
        if response.status_code == 200:
            result = response.json()
            # pprint(result)
            for all_info in result['response']['items']:
                name = all_info['likes']['count']
                url = all_info['sizes'][-1]['url']
                date = all_info['date']
                if name in photo:
                    x = {f'{name}_{date}': {'date': date, 'url': url}}
                    photo.update(x)
                else:
                    x = {name: {'date': date, 'url': url}}
                    photo.update(x)
            pprint(photo)
        return photo


# ЗАГРУЗКА ФОТО ИЗ СЛОВАРЯ НА ЯДИСК ЧЕРЕЗ URL
class YaUploader():

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, file_path):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {"path": file_path, "overwrite": "true"}
        response = requests.get(url=upload_url, headers=headers, params=params)
        pprint(response.json())
        return response.json()

    def upload_file_to_disk(self, file_path, limit=19):
        headers = self.get_headers()
        index = 0
        for name, info in tqdm(photo.items(), desc='Upload Photos from url to yadisk'):
            file_name = name
            file_url = info['url']
            index += 1
            if index > limit:
                break
            upload_params = {'path': f'{file_path}/{file_name}', 'url': f'{file_url}'}
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            response = requests.post(url=url, params=upload_params, headers=headers)



if __name__ == '__main__':
    file_path = 'netology/photo'
    token = ''
    VkUser.get_user_photo()
    uploader = YaUploader(token)
    uploader.upload_file_to_disk(file_path)


# ПОЛУЧЕНИЕ ДАННЫХ С ЯДИСКА О ЗАГРУЖЕННЫХ ФОТО
token = ''


def get_headers(token):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token)
    }


def ya_metadata():
    path = '/netology/photo/'
    url = f'https://cloud-api.yandex.net/v1/disk/resources'
    headers = get_headers(token)
    params = {'path': path, 'token': token,
              'fields': '_embedded.items.name,_embedded.items.size,_embedded.items.modified,'
                        '_embedded.items.mime_type,_embedded.items.path'}
    response = requests.get(url=url, headers=headers, params=params)
    return response.json()


# ЗАПИСЬ ПОЛУЧЕННЫХ ДАННЫХ В ФАЙЛ JSON
with open('photo.json', 'w') as file:
    json.dump(ya_metadata(), file, ensure_ascii=False, indent=2)
