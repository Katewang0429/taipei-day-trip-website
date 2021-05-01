from flask import *
import pymysql
import pymysql.cursors


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False

connection = pymysql.connect(host="localhost",
                             user="kate",
                             password="K@wang01",
                             db="website",
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/attraction/<id>", methods=['GET', 'POST'])
def attraction(id):
    # return render_template("attraction.html")
    if request.method == "POST":
        pass

    try:
        cursor = connection.cursor()
        sql = "SELECT * FROM attractions WHERE _id = {0};".format(id)
        cursor.execute(sql)
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
        cursor = connection.cursor()
        sql = "SELECT * FROM attractions WHERE xbody LIKE '%" + keyword + \
            "%' order by _id;" if keyword != None else "SELECT * FROM attractions order by _id;"
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()

        if data:
            # print(data)
            next_page = 0
            count = 1
            attraction = []
            result = []
            for item in data:

                attraction.append({
                    "id": str(item["_id"]),
                    "name": item["stitle"],
                    "category": item["CAT1"],
                    "description": item["xbody"],
                    "address": item["address"],
                    "transport": item["info"],
                    "mrt": item["MRT"],
                    "latitude": str(item["latitude"]),
                    "longitude": str(item["longitude"]),
                    "images": item["file"]
                })

                count += 1
                if count % 13 == 0:
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
                "message": "查無任何配對資料"
            }

    except Exception as e:
        result = {
            "error": True,
            "message": "伺服器內部錯誤: " + str(e)
        }

    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
