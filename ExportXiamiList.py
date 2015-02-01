
from bs4 import BeautifulSoup
from tkinter import *
import math
import re
import os
import urllib.request


def print_log(where,content):
	where.insert(END,content)
	where.see(END)

def open_link(link):
	request = urllib.request.Request(link)
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
	try:
		html = urllib.request.urlopen(request).read()
		return html
	except urllib.error.HTTPError as err:
		if err.code == 404:
			errorCode = str(err) + "\n链接错误，请重新校对链接"
		else:
			errorCode = str(err) + "\n虾米歌单网页打开失败，请重新校对链接或稍后再试"
		print_log(log,errorCode)		

def get_page_song(soup,pageSongList):
	list = soup.find(attrs={"class": "track_list"}).find_all('td',class_="song_name")
	for song in list:
		songInfo =  str(song).split('</a>')
		songtitle = re.search(r'title="(?P<name>.*)">',songInfo[0])
		songName = songtitle.group('name')
		artistNameList = []

		for i in range(1,len(songInfo)-1):
			artisttitle = re.search(r'class="artist_name"(?P<artisthref>.*)title="(?P<artist>.*)">',songInfo[i])

			if artisttitle:
				artistNameList.append(artisttitle.group('artist'))
			i = i + 1

		if len(artistNameList) > 1:
			joinname = "、"
			artistName = joinname.join(artistNameList)
		else:
			artistName = artistNameList[0]

		global songSum
		global num
		num = num + 1
		numLog = '('+ str(num) +'/'+ songSum +')'
		songLog = '正在导出'+ numLog +':'+ songName + " - " + artistName+'\n'
		print_log(log,songLog)
		pageSongList.append(artistName + " - " + songName)

def xiamilist():
	userEntryURL = userEntryLink.get()
	try:
		userURL = re.search(r'(?P<link>http:\/\/www.xiami.com\/space\/lib-song\/u\/\d+)\D*',userEntryURL)
		userURL = userURL.group('link')
	except AttributeError:
		errorCode = '链接错误，请重新校对链接'
		print (errorCode)
		
	songList = []
	websoup = BeautifulSoup(open_link(userURL))

	songSumSoup = websoup.find(attrs={'class':'all_page'})

	global songSum
	songSum = re.search(r'共(?P<sum>\d+)条',str(songSumSoup))
	songSum = songSum.group('sum')
	global num
	num = 0

	get_page_song(websoup,songList)
	# get other page song
	pageNum = math.ceil(int(songSum)/25)
	if pageNum > 1 :
		for i in range(2,pageNum+1):
			XiamiPageURL = userURL + "/page/" + str(i)
			pagesoup = BeautifulSoup(open_link(XiamiPageURL))
			get_page_song(pagesoup,songList)

	#---------------------------
	# create songlist.xml
	#---------------------------
	filenamesoup = websoup.find('head').find('title')
	filename = str(filenamesoup.text) + '.kgl'

	from xml.dom import minidom
	doc = minidom.Document()
	doclsit = doc.createElement("List")
	doclsit.setAttribute('ListName',filename)
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
	completeNotice = '*******已完成！*******\n可以将该程序所在文件夹下的'+ filename +'导入到网易云音乐了！'
	print_log(log,completeNotice)

import threading

def onclick():
	exportThread = threading.Thread(target=xiamilist)
	exportThread.start()


root = Tk()
root.title('导出虾米歌单')
root.config(height=480)

title = Label(root,text='导出虾米歌单',font='微软雅黑 -23 bold',fg='#fa8723')
title.pack()

userEntry = Label(root,width=350)
userEntry.pack(pady=8)
userEntryTitle = Label(userEntry,text='请输入歌单链接')
userEntryTitle.pack(side=LEFT)
userEntryLink = Entry(userEntry,width=50)
userEntryLink.pack(side=LEFT)

# entryExplain = Label(root,wraplength=400,fg='grey',justify='left',text='获取虾米歌单链接方法：登录虾米网页点击顶栏中的「我的音乐」，然后点击「音乐库」下面的「收藏的歌曲」所获得的链接即歌单链接（一定要点击不然链接不对）。\n（正确链接参考 http://www.xiami.com/lib-song/u/123456?spm=xxx）')
# entryExplain.pack()

export = Button(root,width=20,text='导出',command=onclick)
export.pack(pady=8)

readme = '获取虾米歌单链接方法：\n登录虾米网页点击顶栏中的「我的音乐」，然后点击「音乐库」下面的「收藏的歌曲」所获得的链接即歌单链接（一定要点击不然链接不对）。'

log = Text(root)
log.config(width=70,height=12)
log.insert(END,readme)
log.pack(side=LEFT,fill='both')

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT,fill=Y)
scrollbar.config(command = log.yview())
log.config(yscrollcommand=scrollbar.set)


root.mainloop()
