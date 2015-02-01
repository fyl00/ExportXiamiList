# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from tkinter import *
import math
import re
import os
import urllib.request

agent1 = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'
agent2 = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)'

def print_log(where,content):
	where.insert(END,content)
	where.see(END)

def open_link(link,agent):
	request = urllib.request.Request(link)
	request.add_header('User-Agent',agent)
	try:
		html = urllib.request.urlopen(request).read()
		return html
	except urllib.error.HTTPError as err:
		if err.code == 404:
			errorCode = "\n"+str(err) + "\n链接错误，请重新校对链接"
		else:
			errorCode = "\n"+str(err) + "\n虾米歌单网页打开失败，请重新校对链接或稍后再试"
		print_log(log,errorCode)		

def isRealArtist(name):
    name = name.get('title')
    conditionA = (name != '高清MV')
    conditionB = (name != '虾米音乐人')
    return (conditionA and conditionB)

def get_u_song(soup,pageSongList):
	songlist = soup.find('table',class_="track_list").find_all('tr')
	for song in songlist:
		global num
		num += 1
		#check the song's checkbox
		if 'checked="checked"' in str(song.find('td',class_="chkbox")):
			songInfoTemp = song.find('td',class_="song_name")
			songInfo = songInfoTemp.find_all('a')
			songName = songInfo[0].get('title')

			for i in range(1,len(songInfo)):     
				if isRealArtist(songInfo[i]):
					artistNameTemp = songInfo[i].get_text()
					try :
						artistName = artistNameTemp
					except NameError:
						artistName = artistName + '、' + artistNameTemp

			global songSum
				
			numLog = '('+ str(num) +'/'+ songSum +')'
			songLog = '正在导出'+ numLog +':'+ songName + " - " + artistName+'\n'
			print_log(log,songLog)
			pageSongList.append(artistName + " - " + songName)

def get_collect_song(soup,collectSongList):
	songlist = soup.find(attrs={'class':'quote_song_list'}).find_all('li',class_='totle_up')
	songSum = len(songlist)
	num = 0
	for song in songlist:
		num += 1
		#check the song's checkbox
		if 'checked="true"' in str(song.find('span',class_='chk')):
			songInfoTemp = song.find('span',class_='song_name')
			songInfo = songInfoTemp.find_all('a')
			songName = songInfo[0].get('title')
			artistName = songInfo[1].get_text()

			if len(songInfo) >= 3:
			    for i in range(1,len(songInfo)):
			        anotherartistName = songInfo[i-1].get_text()
			        artistName = artistName + '、' +anotherartistName
			numLog = '('+ str(num) +'/'+ str(songSum) +')'
			songLog = '正在导出'+ numLog +':'+ songName + " - " + artistName+'\n'
			print_log(log,songLog)
			collectSongList.append(artistName + " - " + songName)

		

def link_category(link):
	uLink = re.search(r'(?P<link>http:\/\/www.xiami.com\/space\/lib-song\/u\/\d+)\D*',link)
	collectLink = re.search(r'(?P<link>http:\/\/www.xiami.com\/collect\/\d+)\D*',link)
	if (not uLink) and (not collectLink):
		print_log(log,'\n链接错误，请重新校对链接')
	elif uLink:
		url = uLink.group('link')
		category = 'u'
	elif collectLink:
		url = collectLink.group('link')
		category = 'collect'
	return (category,url)

def xiamilist():
	userEntryURL = userEntryLink.get()

	URLInfo = link_category(userEntryURL)
	userURL = URLInfo[1]	
	songList = []
	websoup = BeautifulSoup(open_link(userURL,agent1))
	
	if URLInfo[0] == 'u':
		xmllistname = '虾米红心'
		filename = 'Xiami.kgl'
		songSumSoup = websoup.find(attrs={'class':'all_page'})
		global songSum
		songSum = re.search(r'共(?P<sum>\d+)条',str(songSumSoup))
		songSum = songSum.group('sum')
		global num
		num = 0

		get_u_song(websoup,songList)
		# get other page song
		pageNum = math.ceil(int(songSum)/25)
		if pageNum > 1 :
			for i in range(2,pageNum+1):
				XiamiPageURL = userURL + "/page/" + str(i)
				if (i % 2) == 0:
					pagesoup = BeautifulSoup(open_link(XiamiPageURL,agent1))
				else:
					pagesoup = BeautifulSoup(open_link(XiamiPageURL,agent2))
				get_u_song(pagesoup,songList)

	elif URLInfo[0] == 'collect':
		filenametemp = re.search(r'\D+\/(?P<filename>\d+)',URLInfo[1])
		filename = 'collect_'+str(filenametemp.group('filename'))+'.kgl'
		xmllistname = websoup.find(attrs={'class':'info_collect_main'}).h2.get_text()
		get_collect_song(websoup,songList)

	#---------------------------
	# create songlist.xml
	#---------------------------
	
	from xml.dom import minidom
	doc = minidom.Document()
	doclsit = doc.createElement("List")
	doclsit.setAttribute('ListName',xmllistname)
	doc.appendChild(doclsit)

	def xml_add_song(name):
		docfile = doc.createElement('File')
		filename = doc.createElement('FileName')
		songname= name+".mp3"
		filename.appendChild(doc.createTextNode(songname))
		docfile.appendChild(filename)
		doclsit.appendChild(docfile)

	for song in songList:
		xml_add_song(song)


	f = open(filename,mode='w',encoding='utf-8')
	doc.writexml(f)
	f.close()
	completeNotice = '\n*******已完成！*******\n可以将该程序所在文件夹下的「'+ filename +'」导入到网易云音乐了！\n'
	print_log(log,completeNotice)

import threading

def onclick():
	exportThread = threading.Thread(target=xiamilist)
	exportThread.start()


root = Tk()
root.title('导出虾米歌单')
root.config(height=480,pady=10)

title = Label(root,text='导出虾米歌单',font='微软雅黑 -23 bold',fg='#fa8723')
title.pack()

userEntry = Label(root,width=350)
userEntry.pack()
userEntryTitle = Label(userEntry,text='歌单或精选集链接')
userEntryTitle.pack(side=LEFT)
userEntryLink = Entry(userEntry,width=50)
userEntryLink.pack(side=LEFT)
export = Button(root,width=20,text='导出',command=onclick)
export.pack(pady=12)

readme = '获取虾米歌单链接方法：\n登录虾米网页点击顶栏中的「我的音乐」，然后点击「音乐库」下面的「收藏的歌曲」所获得的链接即歌单链接（一定要点击不然链接不对）。\n********************\n歌单正确链接参考 http://www.xiami.com/lib-song/u/123456?spm=xxx\n精选集正确连接参考 http://www.xiami.com/collect/123456?spm=xxx\n********************\n'

log = Text(root)
log.config(width=70,height=15)
log.insert(END,readme)
log.pack(side=LEFT,fill='both')

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT,fill=Y)
scrollbar.config(command = log.yview())
log.config(yscrollcommand=scrollbar.set)


root.mainloop()
