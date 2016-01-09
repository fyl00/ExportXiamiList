# -*- coding: utf-8 -*-
# python 2.7
# env:xiamilist

from flask import Flask,render_template,request,Response,Markup
from xiamilist import xiami


app = Flask(__name__)

import socket
if socket.gethostname() == "SS-MBP.local":
    app.debug = True
else:
    app.debug = False



@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/xml/',methods=['POST','GET'])
def export():
    userLink = request.args.get('XiamiListLink')
    methods = request.method
    usercontent = xiami.xiamisonglist(userLink)
    log = usercontent['log']
    xml = usercontent['xmlContent']
    xml = xml.replace('&',u'、')
    return render_template('xml.html',log=log,xml=xml)


if __name__ == '__main__':
    app.run()
