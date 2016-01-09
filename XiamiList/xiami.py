# -*- coding: utf-8 -*-

from xml.dom import minidom
import math
import re
import os
import json

from bs4 import BeautifulSoup
import requests

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
				# for index, cookie in enumerate(self.session.cookies):
				# 	print ('[',index, ']',cookie)
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
					TheData['log'] = '登录虾米时发生未知错误'


			st = jdata['content']['data']['st']
			loginURL = 'http://www.xiami.com/accounts/back?st=' + st
			loginResp = self._safe_get(loginURL,
										headers={'Referer':'https://passport.alipay.com/mini_login.htm',
									             'User-agent': 'Mozilla/5.0'})
			return


class XiamiHandle(XiamiRequest):
	def __init__(self,soup=None,link=None,pagecount=None,pagination=None):
		super(XiamiHandle,self).__init__()
		self.songlist = []
		self.soup = soup
		self.pagecount = pagecount
		self.pagination = pagination
	def get_u_song(self):
		songListSoup = self.soup.find('table',class_="track_list").find_all('tr')
		if songListSoup:
			for song in songListSoup:
				#check the song's checkbox
				# if 'checked="checked"' in str(song.find('td',class_="chkbox")):
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
				# songLog = '正在导出第(%s/%s)页:%s - %s\n' %(self.pagination,self.pagecount,songName.encode('utf-8'),artistName.encode('utf-8'))
				# TheData['log'] = songLog
				# print TheData['log']
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
				    for i in range(2,len(songInfo)):
				        anotherartistName = songInfo[i].get_text()
				        artistName = artistName + u'、' +anotherartistName
				# numLog = '('+ str(num) +'/'+ str(songSum) +')'
				# songLog = u'正在导出'+ numLog +':'+ songName + " - " + artistName+'\n'
				# TheData['log'] = songLog
				# print TheData['log']
				self.songlist.append(artistName + " - " + songName)

	def link_category(self,link):
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
		return (category,url)

	def create_songlist_xml(self,listname):
		list = ''
		for song in self.songlist:
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
		self.soup = BeautifulSoup(self._safe_get(userURL,headers={'User-agent': 'Mozilla/5.0'}).content)
        
		if URLInfo[0] == 'u':
			xmllistname = u'虾米红心'
			xmlFileName = 'Xiami.kgl'
			songSumSoup = self.soup.find(attrs={'class':'all_page'})
			songSum = re.search(r'共(?P<sum>\d+)条',str(songSumSoup))
			songSum = songSum.group('sum')

			# if int(songSum) > 500 :
			# 	print_log(log,"由于需要，正在登录虾米，请等待……")
			# 	XiamiLogin().login_xiami('PleaseEnterUsername','PleaseEnterPassword')

			self.pagecount = int(math.ceil(int(songSum)/25))
			self.pagination = 1
			self.get_u_song()
			# get other page song

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
							pageLog = u"已为您抓取 %s 页歌曲，由于虾米网页 Bug ，此页之后网页上已经没有歌曲了。" %str(i)
							TheData['log'] = pageLog
							TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
							return TheData

					except Exception as err:
						notice = u"抓取到" + str(i) + u"页时发生错误("+ str(err) +u")，请重新校对链接或稍后再试。"
						TheData['log'] = notice
						TheData['xmlContent'] = self.create_songlist_xml(xmllistname)
						return TheData

		elif URLInfo[0] == 'collect':
			filenametemp = re.search(r'\D+\/(?P<filename>\d+)',URLInfo[1])
			xmlFileName = 'collect_'+str(filenametemp.group('filename'))+'.kgl'
			xmllistname = self.soup.find(attrs={'class':'info_collect_main'}).h2.get_text()
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
