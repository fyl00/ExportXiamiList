# -*- coding: utf-8 -*-

from xml.dom import minidom
import math
import re
import os
import json

import requests
from lxml import html,etree

TheData = {}


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
                output_log = '打开链接时发生错误\n'+str(e)+"\n请等下再试……"
                TheData['log'] = output_log
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
                output_log = '提交数据时发生错误\n'+str(e)+"\n正在重试……"
                TheData['log'] = output_log
                continue

            return data


class XiamiLink(object):

    def __init__(self, url):
        self.url = url

    @property
    def is_collect(self):
        user_regx = re.search(r'(?P<link>http://www.xiami.com/space/lib-song/u/\d+)\D*', self.url)
        collect_regx = re.search(r'(?P<link>http://www.xiami.com/collect/\d+)\D*', self.url)
        if (not user_regx) and (not collect_regx):
            print("\n链接错误，请重新校对链接")
        elif user_regx:
            return False
        elif collect_regx:
            return True
        return None


class XiamiHandle(XiamiRequest):
    def __init__(self, soup=None, pagecount=None):
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

    def create_songlist_xml(self, listname):

        root = etree.Element("List", ListName=listname)
        for song in self.songs:
            songname = song+".mp3"
            file_node = etree.SubElement(root, "File")
            name_node = etree.SubElement(file_node, "FileName")
            name_node.text = songname
        return etree.tostring(root)

    def get_list(self, url):
        link = XiamiLink(url)
        self.tree = html.fromstring(self._safe_get(url).text)

        if not link.is_collect:
            xmllistname = u'虾米红心'

            # song_sum = 0
            # page_sum_nodes = self.tree.xpath(".//div[@class='all_page']")
            # if page_sum_nodes:
            #     song_sum_re = re.search(r'共(?P<sum>\d+)条', html.tostring(page_sum_nodes[0]))
            #     if song_sum_re and song_sum_re.group("sum"):
            #         song_sum = song_sum_re.group("sum")

            while self.isPageExistedSong:
                self.pagination += 1
                page_url = url + "/page/" + str(self.pagination)
                try:
                    resp = self._safe_get(page_url,
                                          headers={'User-agent': 'Mozilla/5.0'})
                    self.tree = html.fromstring(resp.text)
                    self.isPageExistedSong = self.get_u_song()
                except Exception as err:
                    print("在抓取 %s 页时发生错误\n\t%s" % (self.pagination, err))
                    # TheData['log'] = notice
                    TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
                    return TheData
                pass

        else:
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
    XiamiRequest()
    # userEntryURL = raw_input(link)
    result = XiamiHandle().get_list(link)
    return result

if __name__ == "__main__":
    XiamiHandle().create_songlist_xml()
