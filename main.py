import json

import requests
from pprint import pprint
import time
from tqdm import tqdm

photo = {}


# ПОЛУЧЕНИЕ ФОТО ИЗ ВК И СОХРАНЕНИЕ ИХ В СЛОВАРЬ
class VkUser:
    def __init__(self, vk_token):
        self.vk_token = vk_token

    def id_user(self, vk_token):
        url = 'https://api.vk.com/method/users.get'
        params = {'access_token': vk_token, 'v': '5.131'}
        response = requests.get(url=url, params=params)
        pprint(response.json())

    def get_user_photo(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': 17181069, 'album_id': 'profile', 'photo_sizes': 1, 'access_token': vk_token, 'v': '5.131',
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
class YaUploader:
    def __init__(self, ya_token):
        self.ya_token = ya_token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.ya_token)
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

    def set_layer(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        path = 'netology/vk_photo'
        headers = self.get_headers()
        params = {'path': path, 'token': ya_token}
        response = requests.put(url=url, headers=headers, params=params)

    def ya_metadata(self):
        path = '/netology/vk_photo/'
        url = f'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': path, 'token': ya_token,
                  'fields': '_embedded.items.name,_embedded.items.size,_embedded.items.modified,'
                            '_embedded.items.mime_type,_embedded.items.path'}
        response = requests.get(url=url, headers=headers, params=params)
        return response.json()


if __name__ == '__main__':
    file_path = 'netology/vk_photo'
    ya_token = ''
    vk_token = ''
    VkUser(vk_token=vk_token).get_user_photo()
    uploader = YaUploader(ya_token)
    uploader.set_layer()
    uploader.upload_file_to_disk(file_path)
    # ЗАПИСЬ ПОЛУЧЕННЫХ ДАННЫХ В ФАЙЛ JSON
    with open('photo.json', 'w') as file:
        json.dump(uploader.ya_metadata(), file, ensure_ascii=False, indent=2)