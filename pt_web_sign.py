#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import webbrowser

from bottle import Bottle, run, error, static_file, request

app = Bottle()
pt_info = {}


@app.route('/', method='GET')
def index():
    return static_file('index.html', './')


@app.route('/static/<file_type:re:css|js|fonts>/<filename:path>', method='GET')
def server_static(file_type, filename):
    return static_file(filename, root='static/' + file_type)


@app.route('/data', method='GET')
def get_data():
    global pt_info
    pt_info = load_data()
    # save_data(data)
    return pt_info


@app.route('/update', method='POST')
def update_time():
    global pt_info
    t_data = json.loads(request.forms.data)
    for val in t_data:
        for pt in pt_info["data"]:
            if int(val["id"]) == pt["id"]:
                pt["lastdate"] = val["time"]
                break
    save_data(pt_info)
    return {"code": 0, "msg": "update data successfully.", "data": t_data}


@app.route('/add', method='GET')
def add():
    global pt_info
    t_data = {
        "id": len(pt_info["data"]) + 1,
        "name": request.query.name,
        "url": request.query.url,
        "signin": 0,
        "lastdate": request.query.lastdate,
        "status": True,
        "desc": request.query.desc
    }
    pt_info["data"].append(t_data)
    save_data(pt_info)
    return {"code": 0, "msg": "add site successfully.", "data": t_data}


@app.route('/update/<t_index:int>', method='GET')
def update_info(t_index):
    global pt_info
    for val in pt_info["data"]:
        if val["id"] == t_index:
            val["name"] = request.query.name
            val["url"] = request.query.url
            if request.query.status == "1":
                val["status"] = True
            else:
                val["status"] = False
            val["lastdate"] = request.query.lastdate
            val["desc"] = request.query.desc
            break
    save_data(pt_info)
    return {"code": 0, "msg": "update data successfully.", "data": val}


@app.route('/update/status/<t_index:int>', method='GET')
def update_status(t_index):
    global pt_info
    for val in pt_info["data"]:
        if val["id"] == t_index:
            val["status"] = not val["status"]
            break
    save_data(pt_info)
    return {"code": 0, "msg": "update status successfully."}


@app.route('/delete/<t_index:int>', method='GET')
def delete(t_index):
    global pt_info
    for val in pt_info["data"]:
        if val["id"] == t_index:
            val["delete"] = True
            break
    save_data(pt_info)
    return {"code": 0, "msg": "delete successfully."}


@error(404)
def error404():
    return 'Nothing here, sorry'


def get_diff_days(start):
    start_sec = time.mktime(time.strptime(start, '%Y-%m-%d %H:%M:%S'))
    end_sec = time.time()
    diff_hour = int((end_sec - start_sec) / (60 * 60))
    return str(int(diff_hour / 24)) + "天" + str(int(diff_hour % 24)) + "小时"


def load_data():
    with open('data/data.json', 'r', encoding='UTF-8') as f:
        res = json.load(f)
    # 添加字段
    # for i in range(len(res["data"])):
    #     res["data"][i]["desc"] = ""
    for val in res["data"]:
        val["pasttime"] = get_diff_days(val["lastdate"])
    return res


def save_data(info):
    with open('data/data.json', 'w', encoding='UTF-8') as f:
        json.dump(info, f)
        f.flush()


if __name__ == "__main__":
    webbrowser.open_new_tab('http://127.0.0.1:8080')
    run(app, host='localhost', port=8080)
