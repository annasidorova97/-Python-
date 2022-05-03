import json

import requests
from pprint import pprint
import datetime

with open('token_vk.txt') as file:
    token_vk = file.read()

token_yandex = ""


def get_user(id: int):
    url_vk = 'https://api.vk.com/method/users.get'
    params = {'access_token': token_vk, 'user_ids': str(id), 'v': '5.131', 'fields': 'followers_count,sex'}
    responce = requests.get(url_vk, params=params)
    pprint(responce.json())


def get_photos_list(id:int):
    url_vk = 'https://api.vk.com/method/photos.get'
    params = {'access_token': token_vk, 'user_id': str(id), 'v': '5.131', 'album_id': 'profile', 'rev': 1, 'extended': 1, 'count': 5}
    responce = requests.get(url_vk, params=params)
    photos_list = []
    likes_list = []
    for item in responce.json()['response']['items']:
        max_size = 0
        photo_dict = {}
        for size in item['sizes']:
            if int(size['width']) > max_size:
                max_size = int(size['width'])
                photo_dict['size'] = size['type']
                photo_dict['url'] = size['url']
        photo_dict['likes'] = str(item['likes']['count'])
        photo_dict['date'] = datetime.datetime.utcfromtimestamp(item['date']).strftime('%d-%m-%Y %H:%M:%S')
        photos_list.append(photo_dict)
        likes_list.append(str(item['likes']['count']))
    return photos_list, likes_list


def creating_json(data):
    with open('result.json', 'w') as file:
        json.dump(data, file, indent=2)


def get_headers():
    return {
        'Content-Type': 'application/json',
        'Authorization': f'OAuth {token_yandex}'
    }


def creating_new_folder(folder_path):
    request_url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = get_headers()
    params = {"path": folder_path}
    response = requests.put(request_url, headers=headers, params=params)
    response.raise_for_status()
    if response.status_code == 201:
        print("New folder created successfully")


def uploading_to_yandex_disk_by_url(id: int):
    creating_new_folder('new_folder')
    photo_list, like_list = get_photos_list(id)
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = get_headers()
    json_list = []
    for photo in photo_list:
        json_dict = {}
        json_dict['size'] = photo['size']
        json_list.append(json_dict)
        if like_list.count(photo['likes']) == 1:
            params = {"url": photo['url'], "path": f"new_folder/{photo['likes']}.jpeg"}
            response = requests.post(upload_url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 202:
                print(f"{photo_list.index(photo)+1} out of {len(photo_list)} photo uploaded successfully")
                json_dict['file_name'] = f'{photo["likes"]}.jpeg'
        else:
            params = {"url": photo['url'], "path": f"new_folder/{photo['likes']} {photo['date'][:10]}.jpeg"}
            response = requests.post(upload_url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 202:
                print(f"{photo_list.index(photo)+1} out of {len(photo_list)} photo uploaded successfully")
                json_dict['file_name'] = f"{photo['likes']} {photo['date'][:10]}.jpeg"
    creating_json(json_list)


if __name__ == '__main__':
    uploading_to_yandex_disk_by_url(174097846)

