from bs4 import BeautifulSoup
import requests
import base64
from io import BytesIO
from PIL import Image
from pytesseract import image_to_string

url = "http://challenge01.root-me.org/programmation/ch8/"

session = requests.session()
flag = False

while not flag:
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    img_bytes = soup.find("img").attrs['src'].split(",")[-1]
    # from bytes to string
    img_string = BytesIO(base64.b64decode(img_bytes))
    # open with pillow
    image = Image.open(img_string)
    # strip all garbage from result like commas, dots etc
    answer = "".join(elem for elem in image_to_string(image, lang="eng") if elem.isalnum())
    print("[*] Sending: " + answer)

    # submit form
    response = session.post(url, data={"cametu": answer})
    soup = BeautifulSoup(response.text, 'lxml')
    result = soup.find_all("p")
    # check results
    if len(result) == 2:
            # get flag
            result = result[1].get_text().split()[-1]
            print(f"\n[+] Flag: {result}")
            flag = True
    else:
        print("[-] Not Found. Trying next")
