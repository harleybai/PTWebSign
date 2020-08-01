#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import requests
from bs4 import BeautifulSoup


def get_html(url, code="utf-8"):
    if url == "":
        return False, ""
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = code
        return True, r.text
    except requests.RequestException:
        e_type, e_val, e_stack = sys.exc_info()
        return False, e_val


def parser(html, link):
    res = {}
    soup = BeautifulSoup(html, "html.parser")
    # 1. B站
    if re.search(r'www.bilibili.com', link):
        res['title'] = soup.find('span', {'class': 'media-info-title-t'}).getText()
        res['pic'] = soup.find('div', {'class': 'review-edit-header'}).find('img').get('src')
        for s in soup.find('div', {'class': 'media-info-time'}).findAll('span'):
            if re.search('周', s.getText()):
                res.update(parser_play_time(s.getText()))

    # 2. 腾讯视频
    elif re.search(r'v.qq.com', link):
        res['title'] = soup.find('h1', {'class': 'video_title_cn'}).find('a').getText()
        res['pic'] = soup.find('div', {'class': 'container_inner'}).find('img', {'class': 'figure_pic'}).get('src')
        if soup.find('a', {'class': 'score_db'}):
            res['douban'] = soup.find('a', {'class': 'score_db'}).get('href')
        for s in soup.find('div', {'class': 'video_type video_type_even cf'}).findAll('span', {'class': 'type_txt'}):
            if re.search('周', s.getText()) and re.search('更', s.getText()):
                res.update(parser_play_time(s.getText()))

    # 3. 豆瓣
    elif re.search(r'movie.douban.com', link):
        res['title'] = soup.find('h1').find('span').getText()
        res['pic'] = soup.find('div', {'id': 'mainpic'}).find('img').get('src')
        res['date'] = soup.find('span', {'class': 'pl'}, True, '上映日期:').findNextSibling().getText()
        res['douban'] = link

    # 格式化&返回
    # format pic
    if 'pic' in res.keys():
        res['pic'] = res['pic'].startswith('//') and 'https:' + res['pic'] or res['pic']
    # format date
    if 'date' in res.keys():
        match = re.search(r'\d{4}-\d{2}-\d{2}', res['date'])
        res['date'] = match and match.group() or ""
    # format douban
    if 'douban' in res.keys():
        match = re.search(r'subject/\d+', res['douban'])
        res['douban'] = match and 'https://movie.douban.com/' + match.group() or ""

    return res


def parser_play_time(play_time):
    res = {'week': [], 'time': ""}
    week_en = {
        '一': 'Monday',
        '二': 'Tuesday',
        '三': 'Wednesday',
        '四': 'Thursday',
        '五': 'Friday',
        '六': 'Saturday',
        '日': 'Sunday'
    }
    match1 = re.search(r'\d+:\d+', play_time)
    match2 = re.search(r'(\d+)点', play_time)
    if match1:
        res['time'] = match1.group()
    elif match2:
        res['time'] = match2.groups()[0] + ":00"

    reg = [r'周(.)(至周(.))?', r'周(.)(、(.))?']
    for r in reg:
        match = re.search(r, play_time, re.M | re.I)
        if match:
            for m in match.groups():
                if m is not None and m in week_en.keys():
                    res['week'].append(week_en[m])
    res['week'] = list(set(res['week']))

    return res


if __name__ == "__main__":
    print(parser_play_time('每周日10点更1集，会员抢先看'))
