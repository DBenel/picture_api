from sqlalchemy import create_engine
import json
import os

with open(os.getcwd()+"/application/config/credentials.json","r") as f:
    config = json.load(f)
user = config["mysql_credential"]["user"]
password = config["mysql_credential"]["password"]
host = os.environ.get("MYSQL_HOST")
ddbb = config["mysql_credential"]["database"]

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{ddbb}")

def insert_pictures(pic_path, pic_date):
    
    try:
        with engine.connect() as conn:
            conn.execute(f"INSERT INTO pictures (path, date)  VALUES ('{pic_path}', '{pic_date}')")
            conn.execute("COMMIT;")
            result = conn.execute(f"SELECT id FROM pictures WHERE path LIKE '{pic_path}' AND date LIKE '{pic_date}'")
            row = result.fetchone()[0]
        print("Se guardo imagen en MySQL")
    except engine.connect.Error as err:
        print("Error on insert pictures:{}".format(err))
        return make_response({"description": "Error en la imagen"}, 400)
    
    return row

def insert_tags(pic_id, tags_dic, tag_date):
    try:
        with engine.connect() as conn:
            for(tag, confidence) in tags_dic:
                conn.execute(f"INSERT INTO tags (tag, picture_id, confidence, date) VALUES('{tag}', {pic_id}, {confidence}, '{tag_date}')")
        print("Se registraron etiquetas")
    except engine.connect.Error as err:
        print("Error on insert tags:{}".format(err))
        return make_response({"description": "Error en la imagen"}, 400)

def select_pictures(min_date, max_date, tags):
    condition = ""
    if min_date != "" and max_date =="":
        condition = f"WHERE i.date >= '{min_date}'"
    if min_date == "" and max_date !="":
        condition = f"WHERE date(i.date) <= date('{max_date}')"
    if min_date != "" and max_date !="":
        condition = f"WHERE date(i.date) between date('{min_date}') and date('{max_date}')"
    
    if tags != "":
        all_tags = ""
        for t in tags.split(","):
            all_tags += f"'{t}',"
        
        condition += f" AND t.tag IN ({all_tags[:-1]})"
    query = """
        SELECT i.id, i.path, i.date, t.tag, t.confidence FROM pictures i
        INNER JOIN tags t ON i.id = t.picture_id
        {}
        """.format(condition)
    with engine.connect() as conn:
        result = conn.execute(query)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ]
    
    return data

def select_picture(pic_id):
    query = """
        SELECT i.id, i.path, i.date, t.tag, t.confidence FROM pictures i
        INNER JOIN tags t ON i.id = t.picture_id
        WHERE i.id = {}""".format(pic_id)
    with engine.connect() as conn:
        result = conn.execute(query)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ]
    
    return data

def select_tags_aggregate(min_date, max_date):
    condition = ""
    if min_date != "" and max_date =="":
        condition = f"WHERE date >= '{min_date}'"
    if min_date == "" and max_date !="":
        condition = f"WHERE date(date) <= date('{max_date}')"
    if min_date != "" and max_date !="":
        condition = f"WHERE date(date) between date('{min_date}') and date('{max_date}')"
    
    query = """
        SELECT tag, COUNT(picture_id) as n_images, MIN(confidence) as min_confidence,
        MAX(confidence) as max_confidence, AVG(confidence) as mean_confidence
        FROM tags
        {}
        GROUP BY tag
        """.format(condition)
    with engine.connect() as conn:
        result = conn.execute(query)

        columns = result.keys()
        data = [
            dict(zip(columns, row))
            for row in result
        ]
    
    return data