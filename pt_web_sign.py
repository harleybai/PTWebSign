#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import model
import video_parser
import os
import time
import logging
import requests

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


# pt_search
@app.route('/ptsearch', method='GET')
def playlist_page():
    return static_file('ptsearch.html', './static/html')


# play list
@app.route('/play/data', method='GET')
def play_data():
    res = {"code": 0, "msg": "ok", "data": model.get_play()}
    return res


@app.route('/play/info', method='GET')
def play_info():
    t_id = int(request.query.id)
    data = model.get_play_by_id(t_id)
    if len(data) > 0:
        return {"code": 0, "msg": "ok", "data": data[0]}
    return {"code": 0, "msg": "get play info error, not find data id = %s" % t_id, "data": []}


# play add
@app.route('/play/add', method='POST')
def play_add():
    t_data = json.loads(request.forms.data)
    keys = ['pic', 'title', 'type', 'progress', 'week', 'date',
            'time', 'douban', 'bgm', 'video', 'seen_episode']
    for k in keys:
        if k not in t_data:
            return {"code": 1, "msg": "add play info failed.", "data": t_data}
    t_data['pic'] = img_download_play_list(t_data['pic'])
    model.create_play(t_data)
    return {"code": 0, "msg": "add paly info successfully."}


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
    t_seen_episode = request.forms.seen_episode
    # 下载图片更新链接
    data = model.get_play_by_id(t_id)
    try:
        t_pic = img_download_play_list(t_pic)
        sql = "UPDATE t_play SET pic = '%s', title = '%s', progress = '%s', week = '%s', date = '%s', time = '%s', douban = '%s', bgm = '%s', video = '%s', seen_episode = '%s' where id = %d" % (
            t_pic, t_title, t_progress, t_week, t_date, t_time, t_douban, t_bgm, t_video, t_seen_episode, t_id)
        if t_id > 0:
            model.exec_sql(sql)
            return {"code": 0, "msg": "update play info successfully."}
        return {"code": 1, "msg": "update play info error."}
    except Exception as e:
        return {"code": 1, "msg": "Unable to download img: %s" % e}


# play parse
@app.route('/play/parse', method='GET')
def play_parse():
    url = request.query.url.strip()
    ok, html = video_parser.get_html(url)
    if not ok:
        return {"code": -1, "msg": html, "data": {'url': url}}
    return {"code": 0, "msg": "", "data": video_parser.parser(html, url)}


# play delete
@app.route('/play/delete', method='GET')
def play_delete():
    t_id = int(request.query.id)
    model.delete_play_by_id(t_id)
    return {"code": 0, "msg": "delete play info successfully.", "data": {'id': t_id}}


# db backup
@app.route('/play/backup', method='GET')
def backup_db():
    res = model.backup_db()
    return {"code": res[0], "msg": res[1], "data": {}}


@app.route('/pt/data', method='GET')
def get_pt():
    res = {"data": model.get_pt(), "max_days": 10}
    return res


@app.route('/pt/add', method='POST')
def pt_add():
    t_data = json.loads(request.forms.data)
    keys = ['name', 'level', 'keep', 'last_date',
            'link', 'sign_in', 'status', 'desc']
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
    sql = 'UPDATE t_pt SET last_date = \'%s\' where id IN(%s)' % (
        t_data['time'], t_data['id'])
    model.exec_sql(sql)
    return {"code": 0, "msg": "update data successfully.", "data": t_data}


@app.route('/pt/update', method='POST')
def pt_update():
    t_id = int(request.forms.id)
    t_name = request.forms.name
    t_level = request.forms.level
    t_keep = int(request.forms.keep)
    t_link = request.forms.link
    t_status = int(request.forms.status)
    t_desc = request.forms.desc
    sql = "UPDATE t_pt SET name = '%s',level = '%s',keep = '%d', link = '%s', status = %d, desc = '%s' where id = %d" % (
        t_name, t_level, t_keep, t_link, t_status, t_desc, t_id)
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


@app.route('/pt/site/config', method='GET')
def get_site_config():
    with open('./static/json/site.json', 'r') as f:
        res = f.read()
    return res


# common
@app.route('/<file_type:re:css|js|fonts>/<filename:path>', method='GET')
def server_static(file_type, filename):
    return static_file(filename, root='static/' + file_type)


@app.route('/public/<file_type:re:img>/<filename:path>', method='GET')
def server_public(file_type, filename):
    return static_file(filename, root='public/' + file_type)


@error(404)
def error404():
    return 'Nothing here, sorry'


def img_download_play_list(url):
    # 不是外部图片，则不下载
    if not url.startswith('http'):
        return url
    # 保存图片路径
    img_type = url.split('/')[-1].split('.')[-1]
    if img_type not in ['jpg', 'img', 'png', 'webp', 'jiff', 'gif']:
        img_type = 'jpg'
    pic = 'public/img/' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.' + img_type
    if os.path.exists(pic):
        return pic
    # 下载图片
    try:
        rsp = requests.get(url)
        if rsp.status_code == 200:
            with open(pic, 'wb') as file:
                file.write(rsp.content)
            return pic
        else:
            logging.error('requests.get err, status_code：%d' % rsp.status_code)
            return url
    except Exception as e:
        print(e)
        logging.error("download img err, url: %s" % url)
        return url


def directory_init():
    d = ['data', 'public/img']
    for p in d:
        if not os.path.exists(p):
            os.makedirs(p)


if __name__ == "__main__":
    directory_init()
    model.init()
    run(app, host='localhost', port=8080)