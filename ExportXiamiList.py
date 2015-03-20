# -*- coding: utf-8 -*-

from tkinter import *
from xml.dom import minidom
import math
import re
import os
import json
import threading

from bs4 import BeautifulSoup
import requests
from PIL import Image,ImageTk


def print_log(where,content):
	where.insert(END,content)
	where.see(END)

def isRealArtist(name):
    name = name.get('title')
    conditionA = (name != '高清MV')
    conditionB = (name != '虾米音乐人')
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
				outputLog = '打开链接时发生错误\n'+str(e)+"\n正在重试……"
				print_log(log,outputLog)
				print_log(log,*args)
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
						# print ('403 ' + 'update sec=', sec[0])
						continue
			except Exception as e:
			# 失败重试
				outputLog = '提交数据时发生错误\n'+str(e)+"\n正在重试……"
				print_log(log,outputLog)
				continue

			return data


class XiamiLogin(XiamiRequest):
	def __init__(self, username=None, password=None):
		super().__init__()
		self.username = username
		self.password = password

	def login_xiami(self,username,password):
		loginPageReq = self._safe_get('https://passport.alipay.com/mini_login.htm?lang=&appName=xiami&appEntrance=taobao&cssLink=&styleType=vertical&bizParams=&notLoadSsoView=&notKeepLogin=&rnd=0.6477347570091512?lang=zh_cn&appName=xiami&appEntrance=taobao&cssLink=https%3A%2F%2Fh.alipayobjects.com%2Fstatic%2Fapplogin%2Fassets%2Flogin%2Fmini-login-form-min.css%3Fv%3D20140402&styleType=vertical&bizParams=&notLoadSsoView=true&notKeepLogin=true')
		loginPageSoup = BeautifulSoup(loginPageReq.text)
		captcha = ''
		while True:
			
			postdata = {
				'loginId': username,
				'password': password,
				'appName': 'xiami',
				'appEntrance': 'taobao',
				'hsid': loginPageSoup.find('input', {'name': 'hsid'})['value'],
				'cid': loginPageSoup.find('input', {'name': 'cid'})['value'],
				'rdsToken': loginPageSoup.find('input', {'name': 'rdsToken'})['value'],
				'umidToken': loginPageSoup.find('input', {'name': 'umidToken'})['value'],
				'_csrf_token': loginPageSoup.find('input', {'name': '_csrf_token'})['value'],
				'checkCode': captcha,
				}

			loginPostResp = self._safe_post('https://passport.alipay.com/newlogin/login.do?fromSite=0',
				headers={
		                'Referer':'https://passport.alipay.com/mini_login.htm',
		                'User-agent': 'Mozilla/5.0'},
		        data=postdata).text
			
			jdata = json.loads(loginPostResp)


			if jdata['content']['status'] == -1:
				#print ('err: %s' %str(jdata))
				if 'titleMsg' not in jdata['content']['data']:
					continue
				err_msg = jdata['content']['data']['titleMsg']
				if err_msg == u'请输入验证码' or err_msg == u'验证码错误，请重新输入':
					captcha_id = loginPageSoup.find('input', {'name': 'cid'})['value']
					captcha_url = 'http://pin.aliyun.com/get_img?identity=passport.alipay.com&sessionID=%s' % captcha_id
					cf = open(r'captcha.jpg','wb')
					captchaResp = self._safe_get(captcha_url,
						headers={'User-agent': 'Mozilla/5.0'}
						).content
					cf.write(captchaResp)
					cf.close()
					captchatemp = []
					loginINFO = [username,password]
					popupNotice = '验证码错误，请输入下图中的验证码'
					LoginPopup(popupNotice,captchatemp,loginINFO)
					if captchatemp and loginINFO:
						captcha = captchatemp[0]
						username = loginINFO[0]
						password = loginINFO[1]
					continue  # 重新提交一次
				elif '登录名或登录密码不正确' in err_msg:
					captcha_id = loginPageSoup.find('input', {'name': 'cid'})['value']
					captcha_url = 'http://pin.aliyun.com/get_img?identity=passport.alipay.com&sessionID=%s' % captcha_id
					cf = open(r'captcha.jpg','wb')
					captchaResp = self._safe_get(captcha_url,
						headers={'User-agent': 'Mozilla/5.0'}
						).content
					cf.write(captchaResp)
					cf.close()
					captchatemp = []
					loginINFO = [username,password]
					popupNotice = '登录名或登录密码不正确'
					LoginPopup(popupNotice,captchatemp,loginINFO)
					if captchatemp and loginINFO:
						captcha = captchatemp[0]
						username = loginINFO[0]
						password = loginINFO[1]
					continue 
				else:
					print_log(log,'登录虾米时发生未知错误')


			st = jdata['content']['data']['st']
			loginURL = 'http://www.xiami.com/accounts/back?st=' + st
			loginResp = self._safe_get(loginURL,
										headers={'Referer':'https://passport.alipay.com/mini_login.htm',
									             'User-agent': 'Mozilla/5.0'})
			return


class LoginPopup(Toplevel):
	"""docstring for LoginPopup"""
	def __init__(self,notice,captcha,userLogin):
		super(LoginPopup, self).__init__()
		self.captcha = StringVar()
		self.username = StringVar()
		self.password = StringVar()
		self.title("请登录")
		self.config(width=600)

		intro = Label(self,font='微软雅黑 -18 ',fg='#fa8723',text='歌曲较多，且虾米限制了未登录用户请求次数\n请输入绑定了虾米的淘宝账号和密码')
		intro.pack(pady=5,padx=5)

		if notice == '登录名或登录密码不正确':
			logincallback = Label(self,text=notice,fg='#FF3030')
			logincallback.pack(pady=5)

		usernameINFOBox = Label(self)
		usernameINFOBox.pack(pady=3)
		usernameshowBox = Label(usernameINFOBox,text='登录名')
		usernameshowBox.pack(side=LEFT)
		usernameinputBox = Entry(usernameINFOBox,textvariable=self.username)
		usernameinputBox.pack(side=RIGHT)
		usernameinputBox.insert(0,userLogin[0])
		passwordINFOBox = Label(self)
		passwordINFOBox.pack()
		passwordINFOBox.pack(pady=3)
		passwordshowBox = Label(passwordINFOBox,text='登录密码')
		passwordshowBox.pack(side=LEFT)
		passwordinputBox = Entry(passwordINFOBox,textvariable=self.password)
		passwordinputBox.pack(side=RIGHT)
		passwordinputBox.insert(0,userLogin[1])

		if notice == '验证码错误，请输入下图中的验证码':
			logincallback = Label(self,text=notice,fg='#FF3030')
			logincallback.pack(pady=5)

		captchaBox = Label(self)
		captchaBox.pack(pady=5)
		image = Image.open('captcha.jpg')
		captchaImage = ImageTk.PhotoImage(image)
		captchaImageLabel = Label(captchaBox,image=captchaImage)
		captchaImageLabel.pack(side=LEFT)
		captchaEntry = Entry(captchaBox,width=8,font="Helvetica 17",textvariable=self.captcha)
		captchaEntry.pack(side=RIGHT)

		submit = Button(self,text='提交',width=10,command=lambda:self.callback(captcha,userLogin))
		submit.pack(pady=10)
		self.wait_window(self)

	def callback(self,captcha,userLogin):
		captcha.append(self.captcha.get())
		userLogin[0] = self.username.get()
		userLogin[1] = self.password.get()
		self.destroy()


class XiamiHandle(XiamiRequest):
	def __init__(self,soup=None,link=None,pagecount=None,pagination=None):
		super().__init__()
		self.songlist = []
		self.soup = soup
		self.pagecount = pagecount
		self.pagination = pagination
	def get_u_song(self):
		songListSoup = self.soup.find('table',class_="track_list").find_all('tr')
		if songListSoup:
			for song in songListSoup:
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

					songLog = '正在导出第(%s/%s)页:%s - %s\n' %(self.pagination,self.pagecount,songName,artistName)
					print_log(log,songLog)
					self.songlist.append(artistName + " - " + songName)

			return True

		else:
			return False

	def get_collect_song(self):
		songListSoup = self.soup.find(attrs={'class':'quote_song_list'}).find_all('li',class_='totle_up')
		songSum = len(songListSoup)
		num = 0
		for song in songListSoup:
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
				self.songlist.append(artistName + " - " + songName)

	def link_category(self,link):
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

	def create_songlist_xml(self,listname,filename,notice):
		doc = minidom.Document()
		doclsit = doc.createElement("List")
		doclsit.setAttribute('ListName',listname)
		doc.appendChild(doclsit)

		for song in self.songlist:
			fileNode = doc.createElement('File')
			filenameNode = doc.createElement('FileName')
			songname= song+".mp3"
			filenameNode.appendChild(doc.createTextNode(songname))
			fileNode.appendChild(filenameNode)
			doclsit.appendChild(fileNode)

		f = open(filename,mode='w',encoding='utf-8')
		doc.writexml(f)
		f.close()
		endNotice = str(notice) + '\n已抓取的歌曲列表已保存在程序所在文件夹下的「'+ filename +'」，可以将它导入到网易云音乐了！\n'
		print_log(log,endNotice)

	def get_list(self,link):
		URLInfo = self.link_category(link)
		userURL = URLInfo[1]	
		songList = []
		self.soup = BeautifulSoup(self._safe_get(userURL,headers={'User-agent': 'Mozilla/5.0'}).content)
		
		
		if URLInfo[0] == 'u':
			xmllistname = '虾米红心'
			xmlFileName = 'Xiami.kgl'
			songSumSoup = self.soup.find(attrs={'class':'all_page'})
			songSum = re.search(r'共(?P<sum>\d+)条',str(songSumSoup))
			songSum = songSum.group('sum')

			if int(songSum) > 500 :
				print_log(log,"由于需要，正在登录虾米，请等待……")
				XiamiLogin().login_xiami('PleaseEnterUsername','PleaseEnterPassword')

			self.get_u_song()
			# get other page song
			self.pagecount = math.ceil(int(songSum)/25)
			if self.pagecount > 1 :
				for i in range(2,self.pagecount+1):
					self.pagination = i
					XiamiPageURL = userURL + "/page/" + str(i)
					try:
						resp = self._safe_get(XiamiPageURL,
							headers={'User-agent': 'Mozilla/5.0'})
						self.soup = BeautifulSoup(resp.text)

						isContinue = self.get_u_song()
						if not isContinue:
							pageLog = "=== 由于虾米网页 Bug ，从 %s 页开始已经没有歌曲 ===" %str(i)
							print_log(log,pageLog)
							notice = '\n******* 抓取已完成！*******'
							self.create_songlist_xml(xmllistname,xmlFileName,notice)
							return

					except Exception as err:
						errorCode = "\n"+str(err) + "\n虾米歌单网页打开失败，请重新校对链接或稍后再试"
						notice = errorCode + "\n已抓取到" + str(i) + "页，下次可以从这一页开始抓取"
						self.create_songlist_xml(xmllistname,xmlFileName,notice)
						return

		elif URLInfo[0] == 'collect':
			filenametemp = re.search(r'\D+\/(?P<filename>\d+)',URLInfo[1])
			xmlFileName = 'collect_'+str(filenametemp.group('filename'))+'.kgl'
			xmllistname = self.soup.find(attrs={'class':'info_collect_main'}).h2.get_text()
			self.get_collect_song()

		notice = '\n******* 抓取已完成！*******'

		self.create_songlist_xml(xmllistname,xmlFileName,notice)



class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

# #kill the pop up thread when exit by clicking X 

# def killTreading():
# 	t = threading.enumerate()
# 	print (t)
# 	for i in t:
# 		print (i)
# 		StoppableThread().stop

# 	sys.exit()


def xiamilist():
	xiamiReq = XiamiRequest()
	userEntryURL = userEntryLink.get()
	XiamiHandle().get_list(userEntryURL)


def onclick():
	exportThread = threading.Thread(target=xiamilist)
	exportThread.setDaemon(True)
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
# root.protocol('WM_DELETE_WINDOW',killTreading)
root.mainloop()


