from flask import *
import pymysql
import sys
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False

db_settings = {
    "host": "localhost",
    "user": "kate",
    "password": "K@wang01",
    "db": "website",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/attraction/<id>", methods=['GET', 'POST'])
def attraction(id):
    global cursor

    # return render_template("attraction.html")
    if request.method == "POST":
        pass

    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:

            sql = "SELECT * FROM attractions WHERE _id = %s;"
            cursor.execute(sql, (id))
            data = cursor.fetchone()
            cursor.close()

            if data:
                attraction = []
                attraction.append({
                    "id": str(data["_id"]),
                    "name": data["stitle"],
                    "category": data["CAT1"],
                    "description": data["xbody"],
                    "address": data["address"],
                    "transport": data["info"],
                    "mrt": data["MRT"],
                    "latitude": str(data["latitude"]),
                    "longitude": str(data["longitude"]),
                    "images": data["file"]
                })
                result = dict(data=attraction)
            else:
                result = {
                    "error": True,
                    "message": "景點編號不正確"
                }

    except:
        result = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
    finally:
        conn.close()

    return jsonify(result)


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


@app.route("/api/attractions", methods=['GET', 'POST'])
def attractionsAPI():

    if request.method == "POST":
        pass

    page_number = None
    keyword = None
    if 'page' in request.args:
        page_number = int(request.args.get('page', None))
    if 'keyword' in request.args:
        keyword = request.args.get('keyword', None)

    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            if keyword:
                sql = "SELECT * FROM attractions WHERE stitle LIKE %s order by _id;"
                cursor.execute(sql, ("%" + keyword + "%"))
            else:
                sql = "SELECT * FROM attractions order by _id;"
                cursor.execute(sql)

            data = cursor.fetchall()

            if data:
                next_page = 1
                count = 0
                attraction = []
                result = []

                for item in data:
                    images = []
                    for f in item["file"].split("|"):
                        images.append(f)

                    attraction.append({
                        "id": str(item["_id"]),
                        "name": item["stitle"],
                        "category": item["CAT2"],
                        "description": item["xbody"],
                        "address": item["address"],
                        "transport": item["info"],
                        "mrt": item["MRT"],
                        "latitude": str(item["latitude"]),
                        "longitude": str(item["longitude"]),
                        "images": images
                    })

                    count += 1

                    if count == len(data):
                        result.append({
                            "nextPage": None,
                            "data": attraction
                        })
                    elif count % 12 == 0:
                        result.append({
                            "nextPage": next_page,
                            "data": attraction
                        })
                        next_page += 1
                        attraction = []

                result = result[page_number] if page_number != None else result
            else:
                result = {
                    "error": True,
                    "message": "沒有結果"
                }

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        result = {
            "error": True,
            "message": "伺服器內部錯誤: " + str(e) + ", " + str(exc_type) + ", " + str(fname) + ", " + str(exc_tb.tb_lineno)
        }
    finally:
        conn.close()

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
    #app.run(host="127.0.0.1", port=3000, debug=True)
