#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import time
from shutil import copyfile

conn = sqlite3.connect('data/video.db')


def init():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS `t_pt` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `level` VARCHAR(255),
        `keep` TINYINT,
        `last_date` VARCHAR(32),
        `link` VARCHAR(255),
        `sign_in` TINYINT,
        `status` TINYINT,
        `desc` TEXT
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS `t_play` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `pic` VARCHAR(255) NOT NULL,
        `title` VARCHAR(255),
        `type` TINYINT,
        `progress` VARCHAR(32),
        `week` VARCHAR(255),
        `date` VARCHAR(32),
        `time` VARCHAR(32),
        `douban` VARCHAR(255),
        `bgm` VARCHAR(255),
        `video` VARCHAR(255),
        `seen_episode` VARCHAR(32)
        );''')
    conn.commit()


def exec_sql(sql):
    c = conn.cursor()
    c.execute(sql)
    conn.commit()


def create_pt(data):
    c = conn.cursor()
    c.execute('''
           INSERT INTO `t_pt` (`name`,`level`,`keep`,`last_date`,`link`,`sign_in`,`status`,`desc`) VALUES ('%s','%s',%d,'%s','%s',%d,%d,'%s') ;
        ''' % (
        data['name'], data['level'], data['keep'], data['last_date'], data['link'], data['sign_in'], data['status'],
        data['desc']))
    conn.commit()


def delete_pt_by_id(t_id):
    c = conn.cursor()
    c.execute("DELETE FROM t_pt where id = %d" % t_id)
    conn.commit()


def get_pt_by_id(t_id):
    c = conn.cursor()
    cursor = c.execute("SELECT * from t_pt where id = %d" % t_id)
    res = []
    for row in cursor:
        res.append(row)
    return format_pt(res)


def get_pt():
    c = conn.cursor()
    cursor = c.execute("SELECT * from t_pt")
    res = []
    for row in cursor:
        res.append(row)
    return format_pt(res)


def format_pt(data):
    res = []
    for row in data:
        res.append({
            "id": row[0],
            "name": row[1],
            "level": row[2],
            "keep": row[3],
            "last_date": row[4],
            "link": row[5],
            "sign_in": row[6],
            "status": row[7],
            "desc": row[8],
            "past_time": get_diff_days(row[4])
        })
    return res


def get_diff_days(start):
    start_sec = time.mktime(time.strptime(start, '%Y-%m-%d %H:%M:%S'))
    end_sec = time.time()
    diff_hour = int((end_sec - start_sec) / (60 * 60))
    return str(int(diff_hour / 24)) + "天" + str(int(diff_hour % 24)) + "小时"


def create_play(data):
    c = conn.cursor()
    c.execute('''
           INSERT INTO `t_play` (`pic`,`title`,`type`,`progress`,`week`,`date`,`time`,`douban`,`bgm`,`video`,`seen_episode`)
           VALUES ('%s','%s',%d,'%s','%s','%s','%s','%s','%s','%s') ;
        ''' % (data['pic'], data['title'], data['type'], data['progress'], data['week'],
               data['date'], data['time'], data['douban'], data['bgm'], data['video'], data['seen_episode']))
    conn.commit()


def delete_play_by_id(t_id):
    c = conn.cursor()
    c.execute("DELETE FROM t_play where id = %d" % t_id)
    conn.commit()


def get_play_by_id(t_id):
    c = conn.cursor()
    cursor = c.execute("SELECT * from t_play where id = %d" % t_id)
    res = []
    for row in cursor:
        res.append(row)
    return format_play(res)


def get_play():
    c = conn.cursor()
    cursor = c.execute("SELECT * from t_play")
    res = []
    for row in cursor:
        res.append(row)
    return format_play(res)


def format_play(data):
    res = []
    for row in data:
        res.append({
            "id": row[0],
            "pic": row[1],
            "title": row[2],
            "type": row[3],
            "progress": row[4],
            "week": row[5],
            "date": row[6],
            "time": row[7],
            "douban": row[8],
            "bgm": row[9],
            "video": row[10],
            "seen_episode": row[11]
        })
    return res


def backup_db():
    try:
        copyfile('data/video.db', 'data/video_backup.db')
    except IOError as e:
        return [1, "Unable to copy file. %s" % e]
    return [0, "ok"]


if __name__ == "__main__":
    init()
    # print(get_pt_by_id(30))
    print(get_play_by_id(1))
    print(get_play_by_id(2))
    print(get_play_by_id(3))
