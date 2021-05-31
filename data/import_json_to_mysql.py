import pymysql
import os
import json
import requests
import re

# read JSON file which is in the next parent folder
file_path = os.path.realpath(os.path.join(
    os.getcwd(), 'taipei-attractions.json'))

json_data = open(file_path, "r", encoding="utf-8")
json_obj = json.load(json_data)


# do validation and checks before insert
def validate_string(val):
    if val != None:
        if type(val) is int:
            # for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val


# connect to MySQL
con = pymysql.connect(host='localhost', user='kate',
                      passwd='', db='website')

cursor = con.cursor()


# parse json data to SQL insert
for i, item in enumerate(json_obj["result"]["results"]):
    SERIAL_NO = validate_string(item["SERIAL_NO"])
    RowNumber = validate_string(item["RowNumber"])
    info = validate_string(item["info"])
    stitle = validate_string(item["stitle"])
    longitude = validate_string(item["longitude"])
    latitude = validate_string(item["latitude"])
    file_url = item["file"].split("http")
    # 過濾掉值為空的元素
    file_url = list(filter(None, file_url))
    strRegex = r":\/\/\w.+.[J|j][P|p][G|g]$"
    r = re.compile(strRegex)
    file_url = list(filter(r.match, file_url))
    # 前綴加上http
    file_url = ["http" + s for s in file_url]
    # 組合成一個string
    #file_url = '|'.join(file_url)
    #jsonImagePath = validate_string("http" + item["file"].split("http")[1])
    address = validate_string(item["address"])
    langinfo = validate_string(item["langinfo"])
    MRT = validate_string(item["MRT"])
    CAT1 = validate_string(item["CAT1"])
    CAT2 = validate_string(item["CAT2"])
    MEMO_TIME = validate_string(item["MEMO_TIME"])
    REF_WP = validate_string(item["REF_WP"])
    POI = validate_string(item["POI"])
    idpt = validate_string(item["idpt"])
    xbody = validate_string(item["xbody"].replace("\'", "\\'"))
    _id = int(item["_id"])
    xpostDate = validate_string(item["xpostDate"])
    avBegin = validate_string(item["avBegin"])
    avEnd = validate_string(item["avEnd"])

    # 檢查DB是否已存在該筆資料
    searchSql = "SELECT SERIAL_NO FROM attractions WHERE SERIAL_NO = '"+SERIAL_NO+"'"
    # print(searchSql)
    cursor.execute(searchSql)
    has_data = cursor.fetchone()

    # 若已存在就跳過
    if has_data:
        print(
            "This record has been inserted, and then the step is skipped: " + str(has_data[0]))
        continue

    # 將圖片下載至本機電腦，透過語法儲存在DB
    number = 0
    path_list = []
    for url in file_url:
        r = requests.get(url)

        image_name = str(_id)

        pysicalPath = "/var/www/html/taipei-day-trip-website/static/images/{0}-{1}.jpg".format(
            image_name, number)

        with open(pysicalPath, 'wb') as f:
            f.write(r.content)

        host = "204.236.160.113:3000"
        #host = "127.0.0.1:3000"
        temp_path = "http://{0}/static/images/{1}-{2}.jpg".format(
            host, image_name, number)
        path_list.append(temp_path)
        number += 1

    filePath = "|".join(path_list)

    # 若無誤，就執行插入DB語法
    insertSql = "INSERT INTO attractions (SERIAL_NO, RowNumber, info, stitle, longitude, latitude, file, address, langinfo, MRT, CAT1, CAT2, MEMO_TIME, REF_WP, POI, idpt, xbody, _id, xpostDate, avBegin, avEnd) " + \
        "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', {17}, '{18}', '{19}', '{20}')".format(
            SERIAL_NO, RowNumber, info, stitle, longitude, latitude, filePath, address, langinfo, MRT, CAT1, CAT2, MEMO_TIME, REF_WP, POI, idpt, xbody, _id, xpostDate, avBegin, avEnd)

    cursor.execute(insertSql)
    con.commit()

    # print(insertSql)
    print("The insertion of the record has been completed: " +
          str(_id) + ", " + stitle + ", " + CAT2)


con.close()
