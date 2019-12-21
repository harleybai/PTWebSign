#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import model

from bottle import Bottle, run, error, static_file, request

app = Bottle()


# pt
@app.route('/', method='GET')
def index_page():
    return static_file('index.html', './static/html')


# video
@app.route('/video', method='GET')
def video_page():
    return static_file('video.html', './static/html')


# play
@app.route('/playlist', method='GET')
def playlist_page():
    return static_file('playlist.html', './static/html')


# play list
@app.route('/play/data', method='GET')
def play_data():
    res = {"code": 0, "msg": "ok", "data": model.get_play()}
    return res


@app.route('/play/info', method='GET')
def play_delete():
    t_id = int(request.query.id)
    data = model.get_play_by_id(t_id)
    if len(data) > 0:
        return {"code": 0, "msg": "ok", "data": data[0]}
    return {"code": 0, "msg": "get play info error, not find data id = %s" % t_id, "data": []}


# play add
@app.route('/play/add', method='POST')
def play_add():
    t_data = json.loads(request.forms.data)
    keys = ['pic', 'title', 'type', 'progress', 'week', 'date', 'time', 'douban', 'bgm', 'video']
    for k in keys:
        if k not in t_data:
            return {"code": 1, "msg": "add play info failed.", "data": t_data}
    model.create_play(t_data)
    return {"code": 0, "msg": "add paly info successfully.", "data": t_data}


# play update
@app.route('/play/update', method='POST')
def playlist_page_update():
    t_id = int(request.forms.id)
    t_pic = request.forms.pic
    t_title = request.forms.title
    t_progress = request.forms.progress
    t_week = request.forms.week
    t_date = request.forms.date
    t_time = request.forms.time
    t_douban = request.forms.douban
    t_bgm = request.forms.bgm
    t_video = request.forms.video
    sql = "UPDATE t_play SET pic = '%s', title = '%s', progress = '%s', week = '%s', date = '%s', time = '%s', douban = '%s', bgm = '%s', video = '%s' where id = %d" % (
        t_pic, t_title, t_progress, t_week, t_date, t_time, t_douban, t_bgm, t_video, t_id)
    model.exec_sql(sql)
    return {"code": 0, "msg": "update play info successfully."}


# play delete
@app.route('/play/delete', method='GET')
def play_delete():
    t_id = int(request.query.id)
    model.delete_play_by_id(t_id)
    return {"code": 0, "msg": "delete play info successfully.", "data": {'id': t_id}}


@app.route('/pt/data', method='GET')
def get_pt():
    res = {"data": model.get_pt(), "max_days": 10}
    return res


@app.route('/pt/add', method='POST')
def pt_add():
    t_data = json.loads(request.forms.data)
    keys = ['name', 'last_date', 'link', 'sign_in', 'status', 'desc']
    for k in keys:
        if k not in t_data:
            return {"code": 1, "msg": "add site failed.", "data": t_data}
    model.create_pt(t_data)
    return {"code": 0, "msg": "add site successfully.", "data": t_data}


@app.route('/pt/last_date', method='POST')
def pt_update_time():
    t_data = json.loads(request.forms.data)
    if 'id' not in t_data or 'time' not in t_data:
        return {"code": 1, "msg": "update data failed.", "data": t_data}
    sql = 'UPDATE t_pt SET last_date = \'%s\' where id IN(%s)' % (t_data['time'], t_data['id'])
    model.exec_sql(sql)
    return {"code": 0, "msg": "update data successfully.", "data": t_data}


@app.route('/pt/update', method='POST')
def pt_update():
    t_id = int(request.forms.id)
    t_name = request.forms.name
    t_link = request.forms.link
    t_status = int(request.forms.status)
    t_desc = request.forms.desc
    sql = "UPDATE t_pt SET name = '%s', link = '%s', status = %d, desc = '%s' where id = %d" % (
        t_name, t_link, t_status, t_desc, t_id)
    model.exec_sql(sql)
    return {"code": 0, "msg": "update site successfully."}


@app.route('/pt/status', method='GET')
def pt_update_status():
    t_id = int(request.query.id)
    status = int(request.query.status)
    sql = 'UPDATE t_pt SET status = %d where id = %d' % (status, t_id)
    model.exec_sql(sql)
    return {"code": 0, "msg": "update status successfully."}


@app.route('/pt/delete', method='GET')
def pt_delete():
    t_id = int(request.query.id)
    model.delete_pt_by_id(t_id)
    return {"code": 0, "msg": "delete successfully."}


# common
@app.route('/<file_type:re:css|js|fonts>/<filename:path>', method='GET')
def server_static(file_type, filename):
    return static_file(filename, root='static/' + file_type)


@error(404)
def error404():
    return 'Nothing here, sorry'


if __name__ == "__main__":
    model.init()
    run(app, host='localhost', port=8080)
