# -*- coding: utf-8 -*-

from xml.dom import minidom
import math
import re
import os
import json

import requests
from lxml import html,etree

TheData = {}

def isRealArtist(name):
    name = name.get('title')
    conditionA = (name != u'高清MV')
    conditionB = (name != u'音乐人')
    return (conditionA and conditionB)

class XiamiRequest(object):
    header = {'User-Agent': 'Mozilla/5.0',
              'Referer': 'http://img.xiami.com/static/swf/seiya/player.swf?v=1394535902294'}
    def __init__(self):
        self.session = requests.session()

    def _safe_get(self, *args, **kwargs):
        while True:
            try:
                data = self.session.get(*args, **kwargs)

                if data.status_code == 403:
                    sec = re.findall('<script>document.cookie="sec=(.*?);', data.text)
                    if len(sec) != 0:
                        self.session.cookies['sec'] = sec[0]
                        # print ('403 update sec=' + sec[0])
                        continue
            except Exception as e:
            # 失败重试
                outputLog = '打开链接时发生错误\n'+str(e)+"\n请等下再试……"
                TheData['log'] = outputLog
                continue

            return data

    def _safe_post(self, *args, **kwargs):
        while True:
            try:
                data = self.session.post(*args, **kwargs)

                if data.status_code == 403:
                    sec = re.findall('<script>document.cookie="sec=(.*?);', data.text)
                    if len(sec) != 0:
                        self.session.cookies['sec'] = sec[0]
                        print ('403 !' + 'update sec=', sec[0])
                        continue
            except Exception as e:
            # 失败重试
                outputLog = '提交数据时发生错误\n'+str(e)+"\n正在重试……"
                TheData['log'] = outputLog
                continue

            return data

class XiamiHandle(XiamiRequest):
    def __init__(self, soup=None, link=None, pagecount=None):
        super(XiamiHandle, self).__init__()
        self.songs = []
        self.tree = soup
        self.pagecount = pagecount
        self.pagination = 0
        self.isPageExistedSong = True

    def get_u_song(self):
        song_nodes = self.tree.xpath(".//table[@class='track_list'//tr]")
        if song_nodes:
            print("Page: %s" % self.pagination)
            for node in song_nodes:
                name_nodes = node.xpath("td[@class='song_name]/a/@title")
                artist_nodes = node.xpath("td[@class='song_name']/a[@class='artist_name']/@title")
                if name_nodes and artist_nodes:
                    # and name_tmp[0] not in ["高清MV", "音乐人"]
                    song_name = name_nodes[0]
                    artist_name = artist_nodes.join("、")
                    self.songs.append(artist_name + " - " + song_name)
                else:
                    print("get song failed. %s" % [node for node in name_nodes])

            return True
        else:
            print("There's no data from page %s." % self.pagination)
            return False

    def get_collect_song(self):
        song_nodes = self.tree.xpath(".//div[@class='quote_song_list'//li]")
        num = 0
        for node in song_nodes:
            num += 1
            # check the song's checkbox
            if node.xpath("//span[@class='chk']/input[@checked]"):
                song_info_nodes = node.xpath("div//span[@class='song_name']/a")
                if song_info_nodes and len(song_info_nodes) >= 2:
                    song_name = song_info_nodes[0].text.strip()
                    artist_names = [tmp.text.strip() for tmp in range(1, len(song_info_nodes))
                                    if tmp.text.strip() != "MV"]
                    if len(artist_names) > 0:
                        info = artist_names.join("、") + " - " + song_name
                        self.songs.append(info)
            else:
                song_name_nodes = node.xpath("div//span[@class='song_name']")
                if song_name_nodes:
                    song_name = song_name_nodes[0].text.replace("--", "").strip()
                    artist_nodes = song_name_nodes[0].xpath("a")
                    if artist_nodes:
                        artist_names = [artist_node.text for artist_node in artist_nodes]
                        info = artist_names.join("、") + " - " + song_name
                        self.songs.append(info)

    def link_category(self, link):
        uLink = re.search(r'(?P<link>http:\/\/www.xiami.com\/space\/lib-song\/u\/\d+)\D*',link)
        collectLink = re.search(r'(?P<link>http:\/\/www.xiami.com\/collect\/\d+)\D*',link)
        if (not uLink) and (not collectLink):
            TheData['log'] = '\n链接错误，请重新校对链接'
        elif uLink:
            url = uLink.group('link')
            category = 'u'
        elif collectLink:
            url = collectLink.group('link')
            category = 'collect'
        return (category, url)

    def create_songlist_xml(self,listname):
        list = ''
        for song in self.songs:
            songname= song+".mp3"
            filenameNode = '<FileName>'+songname+'</FileName>\n'
            fileNode = '<File>\n'+filenameNode+'</File>\n'
            list += fileNode
        list = '<?xml version="1.0" ?>\n<List ListName="'+listname+'">\n'+list+'</List>'
        return list


    def get_list(self,link):
        URLInfo = self.link_category(link)
        userURL = URLInfo[1]
        songList = []
        self.tree = html.fromstring(self._safe_get(userURL).text)

        if URLInfo[0] == 'u':
            xmllistname = u'虾米红心'
            xmlFileName = 'Xiami.kgl'

            song_sum = 0
            page_sum_nodes = self.tree.xpath(".//div[@class='all_page']")
            if page_sum_nodes:
                song_sum_re = re.search(r'共(?P<sum>\d+)条', html.tostring(page_sum_nodes[0]))
                if song_sum_re and song_sum_re.group("sum"):
                    song_sum = song_sum_re.group("sum")

            while self.isPageExistedSong:
                self.pagination += 1
                XiamiPageURL = userURL + "/page/" + str(self.pagination)
                try:
                    resp = self._safe_get(XiamiPageURL,
                        headers={'User-agent': 'Mozilla/5.0'})
                    self.etree = html.fromstring(resp.text)
                    self.isPageExistedSong = self.get_u_song()
                except Exception as err:
                    notice = u"抓取到" + str(i) + u"页时发生错误("+ str(err) +u")，请重新校对链接或稍后再试。"
                    TheData['log'] = notice
                    TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
                    return TheData
                pass

        elif URLInfo[0] == 'collect':
            name_nodes = self.etree.xpath(".//div[@class='info_collect_main'/h2]")
            xmllistname = "collect.kgl"
            if name_nodes:
                xmllistname = name_nodes[0].text + ".kgl"

            self.get_collect_song()

        notice = u'抓取已完成！'
        TheData['log'] = notice
        TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
        return TheData


def xiamisonglist(link):
    xiamiReq = XiamiRequest()
    # userEntryURL = raw_input(link)
    result = XiamiHandle().get_list(link)
    return result
