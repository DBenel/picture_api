from flask import request, Blueprint, make_response
from application.controllers import controller_picture

bp = Blueprint('pictures', __name__, url_prefix='/')

@bp.post("/register")
def register_image():
    min_confidence = float(request.args.get("min_confidence", 80))
    
    # data input checks
    if not request.is_json or "data" not in request.json:
        return make_response({"description": "Debes incluir una imagen en base64 como un campo llamado data en el body"}, 400)
    else:
        print("data si tiene valor")
    
    b64str = request.json["data"]
    
    response = controller_picture.add_picture(min_confidence, b64str)
    return response

@bp.get("/images")
def get_images():
    min_date = request.args.get("min_date", "")
    max_date = request.args.get("max_date", "")
    tags_list = request.args.get("tags","")
    
    response = controller_picture.get_pictures(min_date, max_date, tags_list)
    return response

@bp.get("/image")
def get_image():
    pic_id = int(request.args.get("id"))

    response = controller_picture.get_picture(pic_id) 
    return response

@bp.get("/tags")
def get_tags():
    min_date = request.args.get("min_date", "")
    max_date = request.args.get("max_date", "")

    response = controller_picture.get_tags_aggregate(min_date, max_date)

    return response