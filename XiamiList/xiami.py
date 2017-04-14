# -*- coding: utf-8 -*-

import re

from lxml import html, etree
from .grabbot import GrabBot
from .tips import LINK_ERROR_TIPS
TheData = {}


class XiamiLink(object):

    def __init__(self, url):
        self.url = url

    @property
    def is_collect(self):
        user_regx = re.search(r"(?P<link>http://www.xiami.com/space/lib-song/u/\d+)\D*", self.url)
        collect_regx = re.search(r"(?P<link>http://www.xiami.com/collect/\d+)\D*", self.url)
        if (not user_regx) and (not collect_regx):
            print(LINK_ERROR_TIPS)
        elif user_regx:
            self.url = user_regx.group("link")
            return False
        elif collect_regx:
            self.url = collect_regx.group("link")
            return True
        return None


class XiamiHandle(object):
    def __init__(self, pagecount=None):
        self.songs = []
        self.tree = None
        self.pagecount = pagecount
        self.pagination = 0
        self.isPageExistedSong = True

    def get_u_song(self):
        song_nodes = self.tree.xpath(".//table[@class='track_list']//tr")
        # print(etree.tostring(song_nodes[1]))
        if len(song_nodes):
            for node in song_nodes:

                name_nodes = node.xpath("td[@class='song_name']/a/@title")
                artist_nodes = node.xpath("td[@class='song_name']/a[@class='artist_name']/@title")
                if name_nodes and artist_nodes:
                    # and name_tmp[0] not in ["高清MV", "音乐人"]
                    song_name = name_nodes[0]
                    artist_name = "、".join(artist_nodes)
                    info = artist_name + " - " + song_name
                    print("-> %s" % info)
                    self.songs.append(info)
                else:
                    print("获取歌曲失败. %s" % [node for node in name_nodes])

            return True
        else:
            print("第 %s 页没有数据." % self.pagination)
            return False

    def get_collect_song(self):
        song_nodes = self.tree.xpath(".//div[@class='quote_song_list']//li")
        for node in song_nodes:
            # check the song's checkbox
            if node.xpath("//span[@class='chk']/input[@checked]"):
                song_info_nodes = node.xpath("div//span[@class='song_name']/a")
                if song_info_nodes and len(song_info_nodes) >= 2:
                    song_name = song_info_nodes[0].text.strip()
                    artist_names = [song_info_nodes[i].text.strip() for i in range(1, len(song_info_nodes))
                                    if song_info_nodes[i].text.strip() != "MV"]
                    if len(artist_names) > 0:
                        info = "、".join(artist_names) + " - " + song_name
                        print("-> %s" % info)
                        self.songs.append(info)
            else:
                song_name_nodes = node.xpath("div//span[@class='song_name']")
                if song_name_nodes:
                    song_name = song_name_nodes[0].text.replace("--", "").strip()
                    artist_nodes = song_name_nodes[0].xpath("a")
                    if artist_nodes:
                        artist_names = [artist_node.text for artist_node in artist_nodes]
                        info = "、".join(artist_names) + " - " + song_name
                        print("-> %s" % info)
                        self.songs.append(info)

    def create_songlist_xml(self, listname):

        root = etree.Element("List", ListName=listname)
        for song in self.songs:
            songname = song+".mp3"
            file_node = etree.SubElement(root, "File")
            name_node = etree.SubElement(file_node, "FileName")
            name_node.text = songname
        etree.ElementTree(root).write("xiami.kgl",
                                      xml_declaration=True,
                                      encoding="utf8",
                                      pretty_print=True)
        return etree.tostring(root)

    def get_list(self, url):
        spider = GrabBot()
        link = XiamiLink(url)
        response = spider.get(url)
        self.tree = html.fromstring(response.text)
        print("抓取歌单：%s" % url)
        if not link.is_collect:
            xmllistname = u'虾米红心'
            while self.isPageExistedSong:
                self.pagination += 1
                page_url = link.url + "/page/" + str(self.pagination)

                print("第 %s 页: %s" % (self.pagination, page_url))
                try:
                    resp = spider.get(page_url)
                    self.tree = html.fromstring(resp.text)
                    self.isPageExistedSong = self.get_u_song()
                except Exception as err:
                    print("在抓取 %s 页时发生错误:\n\t%s" % (self.pagination, err))
                    # TheData['log'] = notice
                    TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
                    return TheData
                pass

        else:
            name_nodes = self.tree.xpath(".//div[@class='info_collect_main']/h2")
            xmllistname = "collect"
            if name_nodes:
                xmllistname = name_nodes[0].text.strip()

            self.get_collect_song()

        notice = u'抓取已完成！'
        TheData['log'] = notice
        self.create_songlist_xml(xmllistname)
        # TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
        return TheData


def xiamisonglist(url):
    result = XiamiHandle().get_list(url)
    return result

if __name__ == "__main__":
    # XiamiHandle().create_songlist_xml()
    user_url = "http://www.xiami.com/space/lib-song/u/2200240?spm=a1z1s.6928797.1561534513.1.U6HtZZ"
    collect_url = "http://www.xiami.com/collect/29594456"
    XiamiHandle().get_list(user_url)
