import os
from pathlib import Path

import qrcode
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("HIDDIFY_URL")
user_proxy_path = os.getenv("PROXY_PATH_FOR_USER_LINK")


class Link:

    def __init__(self, uuid, name, user_id):
        self.user_id = user_id
        self.name = name
        self.uuid = uuid
        self.user_url = f"https://{url}/{user_proxy_path}/{self.uuid}/#{self.name}"


    def generate_qr_code(self):
        filename = f"qr_{self.user_id}_{self.uuid}.png"
        qr_path = Path("qr_code/QR_codes/")
        qr_path.mkdir(parents=True, exist_ok=True)
        qr_dir_path = qr_path / filename


        img = qrcode.make(self.user_url)
        type(img)
        img.save(qr_dir_path)
        return qr_dir_path

    def generate_link(self):
        return self.user_url

if __name__ == '__main__':

    link = Link(uuid="asdlfasodijoiajsdof", name="Fjomi", user_id=1)
    l = link.generate_link()
    qr = link.generate_qr_code()
    print(l)