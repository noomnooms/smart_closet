import requests
import json
import time
from datetime import datetime

def get_to_dbio():

	url = "https://clothes-a7ad.restdb.io/rest/clothes"

	headers = {
	    'content-type': "application/json",
	    'x-apikey': "e9d41e865cfca1db8149878191c1384dc1eee",
	    'cache-control': "no-cache"
	    }

	response = requests.request("GET", url, headers=headers)

	print(response.text)

	return json.loads(response.text)


def post_to_dbio(name,category):

	url = "https://clothes-a7ad.restdb.io/rest/clothes"

	payload = json.dumps( {"name": name,"category": category} )

	headers = {
	    'content-type': "application/json",
	    'x-apikey': "e9d41e865cfca1db8149878191c1384dc1eee",
	    'cache-control': "no-cache"
	    }

	response = requests.request("POST", url, data=payload, headers=headers)

	print(response.text)

def delete_to_dbio(name,category):

    db = get_to_dbio()
    ident = ''
    for outfit in db:
        if outfit['name'] == name:
            ident = outfit['_id']


    url = "https://clothes-a7ad.restdb.io/rest/clothes/{}".format(ident)

    headers = {
        'content-type': "application/json",
        'x-apikey': "e9d41e865cfca1db8149878191c1384dc1eee",
        'cache-control': "no-cache"
        }

    response = requests.request("DELETE", url, headers=headers)

    print(response.text)

if __name__ == '__main__':
    try:
        time.sleep(1)
        print('Database Manager')
        time.sleep(1)
        
        while True:
            mode = input('Choose action: (write number)\n1.Check data from database\n2.Push data from database\n3.Delete data from database\nA: ')
            if mode == '1':
                get_to_dbio()
            elif mode == '2':
                clothes = input('Q: What\'s the outfit\'s name:\nA: ')
                category = input('Q: Is it winter or summer outfit?\nA: ')
                print('.')
                time.sleep(0.5)
                print('.')
                time.sleep(0.5)
                print('.')
                time.sleep(0.5)
                post_to_dbio(clothes, category)
            elif mode == '3':
                clothes = input('Q: What\'s the outfit\'s name:\nA: ')
                category = input('Q: Is it winter or summer outfit?\nA: ')

                delete_to_dbio(clothes, category)
            time.sleep(1)
    except KeyboardInterrupt:
        print('interrupted')
