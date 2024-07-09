import requests

def get_user_unique_id(user_nickname):
    _url = f'https://www.habbo.com.br/api/public/users?name={user_nickname}'
    response = requests.get(_url)
    return response.json()['uniqueId']


def get_groups_id_by_nick(user_uniqueid):
    _url = f'https://www.habbo.com.br/api/public/users/{user_uniqueid}/profile'
    response = requests.get(_url)
    groups = []
    for obj in response.json()['groups']:
        groups.append({'groupName': obj['name'], 'groupId': obj['id']})

    for group in groups:
        print(f'{group}\n')


nickname = input("Enter target's nickname: ")
get_groups_id_by_nick(get_user_unique_id(nickname))
