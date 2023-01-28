from application.models import model_picture
from imagekitio import ImageKit
from flask import make_response
from datetime import datetime
import os
import requests
import uuid
import base64
import json

def read_image(pic_path):
    with open(pic_path, 'rb') as f:
        picture = f.read()
    return base64.b64encode(picture), len(picture)/1024

def request_add_imagekit(config, b64str, new_name):
    try:
        imagekit = ImageKit(
            private_key= config["ImageKit_credential"]["private_key"],
            public_key= config["ImageKit_credential"]["public_key"],
            url_endpoint= config["ImageKit_credential"]["url_endpoint"]
        )

        upload_info = imagekit.upload(file=b64str.encode(), file_name=new_name)
        imag_kit_url = upload_info.response_metadata.raw["url"]
        imag_file_id = upload_info.file_id
        print("Nos conectamos a ImageKit API")
    except:
        print("Error with ImageKit API")
        return make_response({"description": "Error en la imagen"}, 400)
    else:
        
        return imag_kit_url, imag_file_id

def request_delete_imagekit(config, imag_file_id):
    imagekit = ImageKit(
        private_key= config["ImageKit_credential"]["private_key"],
        public_key= config["ImageKit_credential"]["public_key"],
        url_endpoint= config["ImageKit_credential"]["url_endpoint"]
    )
    delete = imagekit.delete_file(file_id=imag_file_id)
    delete

def request_imagga(config, min_confidence, img_url):
    try:
        api_key = config["Imagga_credential"]["api_key"]
        api_secret = config["Imagga_credential"]["api_secret"]

        response = requests.get(f"https://api.imagga.com/v2/tags?image_url={img_url}", auth=(api_key, api_secret))
        tags_list = [
            (t["tag"]["en"], float(t["confidence"]))
            for t in response.json()["result"]["tags"]
            if float(t["confidence"]) > min_confidence
        ]
        print("Nos conectamos a Imagga API")
    except requests.exceptions.RequestException as err:
        print("Error with Imagga API:{}".format(err))
        return make_response({"description": "Error en la imagen"}, 400)
    else:
        return tags_list


def add_picture(min_confidence, b64str):
    new_name = str(uuid.uuid4())+".jpg"
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.getcwd()+"/application/config/credentials.json","r") as f:
        config = json.load(f)
    
    pic_path = config["main_path"] + "/imagens/"+date_time[:10]+"/"+new_name

    try:
        imgr = base64.b64decode(b64str)
        os.makedirs(os.path.dirname(pic_path), exist_ok=True)
        with open(pic_path, "wb") as f:
            f.write(imgr)
        print("Se guardo imagen en disco")
    except:
        print("Unable to write imagen")
        return make_response({"description": "Error en la imagen"}, 400)

    try:
        pic_id = model_picture.insert_pictures(pic_path, date_time)
    except:
        return make_response({"description": "Error en la imagen"}, 400)

    imag_kit_url, imag_file_id = request_add_imagekit(config, b64str, new_name)

    tag_list = request_imagga(config, min_confidence, imag_kit_url)

    request_delete_imagekit(config, imag_file_id)
    
    model_picture.insert_tags(pic_id, tag_list, date_time)

    picture = {
        "id": pic_id,
        "time_stamp": date_time,
        "tag": [
            t[0]
            for t in tag_list
        ],
        "size": len(b64str.encode())/1024,
        "data": b64str,
    }
    return picture

def get_pictures(min_date, max_date, tags_list):
    
    data = model_picture.select_pictures(min_date, max_date, tags_list)
    
    result_dict = {
        i["id"]: {"id": i["id"],
        "size": i["path"],
        "date": i["date"],
        "tags": [
            {"tag": t["tag"],
            "confidence": t["confidence"]}
            for t in data if t["id"] == i["id"]    
        ]}
        for i in data
    }

    pictures = [
       {**r,
        "size": img[1]
        #"imagen": img[0].decode()
        }
        for r in result_dict.values() if (img:= read_image(r["size"]))
    ]
    
    return pictures

def get_picture(pic_id):

    data = model_picture.select_picture(pic_id)

    result_dict = {
        i["id"]: {"id": i["id"],
        "size": i["path"],
        "date": i["date"],
        "tags": [
            {"tag": t["tag"],
            "confidence": t["confidence"]}
            for t in data if t["id"] == i["id"]    
        ]}
        for i in data
    }

    picture = [{**r,
        "size": img[1],
        "imagen": img[0].decode()}
        for r in result_dict.values() if (img:= read_image(r["size"]))
    ]
    
    return picture

def get_tags_aggregate(min_date, max_date):
    tag_agr = model_picture.select_tags_aggregate(min_date, max_date)
    return tag_agr