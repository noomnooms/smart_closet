import requests
  
URL = 'https://notify-api.line.me/api/notify'
  
def send_message(token, msg, img=None):
    """Send a LINE Notify message (with or without an image)."""
    headers = {'Authorization': 'Bearer ' + token}
    payload = {'message': msg}
    files = {'imageFile': open(img, 'rb')} if img else None
    r = requests.post(URL, headers=headers, params=payload, files=files)
    if files:
        files['imageFile'].close()
    return r.status_code
  
def main():
    import os
    import sys
    import argparse
    token = 'vfWEpfom3zztjRLIj4PMvU34OXVxwQRGu6hn9pVeHaM'
    parser = argparse.ArgumentParser(
        description='Send a LINE Notify message, possibly with an image.')
    parser.add_argument('--img_file', help='the image file to be sent')
    parser.add_argument('message')
    args = parser.parse_args()
    status_code = send_message(token, args.message, args.img_file)
    #print('status_code = {}'.format(status_code))
  
if __name__ == '__main__':
    main()