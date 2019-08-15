#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import webbrowser

from bottle import Bottle, run, error, static_file, request

app = Bottle()

pt_config_path = 'data/pt_config.json'
playlist_config_path = 'data/playlist_config.json'
pt_config = {}
playlist_config = {}

# video
@app.route('/video', method='GET')
def video_page():
    return static_file('video.html', './')

# playlist
@app.route('/playlist', method='GET')
def playlist_page():
    return static_file('playlist.html', './')

# 所有数据
@app.route('/playlist/data', method='GET')
def playlist_data():
    global playlist_config
    if not playlist_config:
        playlist_config = load_data(playlist_config_path, 2)
    return playlist_config

# 某一天数据
@app.route('/playlist/data/<weekday>', method='GET')
def playlist_page_week(weekday):
    global playlist_config
    if not playlist_config:
        playlist_config = load_data(playlist_config_path, 2)
    if weekday not in playlist_config.keys():
        return {}
    return playlist_config[weekday]

# 获取播出的哪几天
@app.route('/playlist/weekday/<id>', method='GET')
def playlist_page_weekday(id):
    global playlist_config
    weekday = []
    resCode = 1
    for key in playlist_config:
        if str(id) in playlist_config[key].keys():
            weekday.append(key)
            resCode = 0
    return {"code": resCode, "msg": "", "data": {'week': weekday}}


def playlist_upsert(t_data):
    global playlist_config
    for week in t_data["week"]:
        if week not in playlist_config.keys():
            playlist_config[week] = {}
        playlist_config[week][t_data["id"]] = t_data
    save_data(playlist_config, playlist_config_path)
    return {"code": 0, "msg": "oprate play info successfully.", "data": t_data}

# 新增数据
@app.route('/playlist/add', method='POST')
def playlist_page_add():
    t_data = json.loads(request.forms.data)
    return playlist_upsert(t_data)

# 更新数据
@app.route('/playlist/update', method='POST')
def playlist_page_update():
    t_data = json.loads(request.forms.data)
    t_data['id'] = str(t_data['id'])
    global playlist_config
    for week in playlist_config:
        if t_data['id'] in playlist_config[week].keys():
            del playlist_config[week][t_data['id']]
    return playlist_upsert(t_data)

# 删除数据
@app.route('/playlist/delete/<id>', method='POST')
def playlist_page_delete(id):
    global playlist_config
    for week in playlist_config:
        if id in playlist_config[week].keys():
            del playlist_config[week][id]
    save_data(playlist_config, playlist_config_path)
    return {"code": 0, "msg": "delete play info successfully.", "data": {'id': id}}

# index
@app.route('/', method='GET')
def index_page():
    return static_file('index.html', './')


@app.route('/data', method='GET')
def get_data():
    global pt_config
    if not pt_config:
        pt_config = load_data(pt_config_path, 1)
    return pt_config


@app.route('/add', method='GET')
def add():
    global pt_config
    t_data = {
        "id": len(pt_config["data"]) + 1,
        "name": request.query.name,
        "url": request.query.url,
        "signin": 0,
        "lastdate": request.query.lastdate,
        "status": True,
        "desc": request.query.desc
    }
    pt_config["data"].append(t_data)
    save_data(pt_config, pt_config_path)
    return {"code": 0, "msg": "add site successfully.", "data": t_data}


@app.route('/update', method='POST')
def update_time():
    global pt_config
    t_data = json.loads(request.forms.data)
    for val in t_data:
        for pt in pt_config["data"]:
            if int(val["id"]) == pt["id"]:
                pt["lastdate"] = val["time"]
                break
    save_data(pt_config, pt_config_path)
    return {"code": 0, "msg": "update data successfully.", "data": t_data}


@app.route('/update/<t_index:int>', method='GET')
def update_info(t_index):
    global pt_config
    for val in pt_config["data"]:
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
    save_data(pt_config, pt_config_path)
    return {"code": 0, "msg": "update data successfully.", "data": val}


@app.route('/update/status/<t_index:int>', method='GET')
def update_status(t_index):
    global pt_config
    for val in pt_config["data"]:
        if val["id"] == t_index:
            val["status"] = not val["status"]
            break
    save_data(pt_config, pt_config_path)
    return {"code": 0, "msg": "update status successfully."}


@app.route('/delete/<t_index:int>', method='GET')
def delete(t_index):
    global pt_config
    for val in pt_config["data"]:
        if val["id"] == t_index:
            val["delete"] = True
            break
    save_data(pt_config, pt_config_path)
    return {"code": 0, "msg": "delete successfully."}

# commom
@app.route('/static/<file_type:re:css|js|fonts>/<filename:path>', method='GET')
def server_static(file_type, filename):
    return static_file(filename, root='static/' + file_type)


@error(404)
def error404():
    return 'Nothing here, sorry'


def get_diff_days(start):
    start_sec = time.mktime(time.strptime(start, '%Y-%m-%d %H:%M:%S'))
    end_sec = time.time()
    diff_hour = int((end_sec - start_sec) / (60 * 60))
    return str(int(diff_hour / 24)) + "天" + str(int(diff_hour % 24)) + "小时"


def load_data(path, config_type):
    with open(path, 'r', encoding='UTF-8') as f:
        res = json.load(f)
    # 添加字段
    # for i in range(len(res["data"])):
    #     res["data"][i]["desc"] = ""
    if config_type == 1:
        for val in res["data"]:
            val["pasttime"] = get_diff_days(val["lastdate"])
    return res


def save_data(info, path):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(info, f)
        f.flush()


if __name__ == "__main__":
    webbrowser.open_new_tab('http://127.0.0.1:8080')
    run(app, host='localhost', port=8080)
