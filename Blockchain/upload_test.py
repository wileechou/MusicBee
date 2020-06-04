import hashlib

from flask import Flask,render_template,jsonify,request
import time
import os
from Blockchain.srModule import Model
from Blockchain.srModule import Database
from PIL import Image
app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['mp3','flac','wma'])

def valid_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
#
#
# def get_songid(song):
#     l = list(song.getFingerprints())
#     l = sorted(l,key=lambda x:x[1])
#     length = len(l)
#     fp_merged = ''
#     temp = l[0][1]
#     for element in l:
#         n = []
#         if element[1] == temp:
#             n.append(element[0])
#         else:
#             n = sorted(n, key=lambda x: x)
#             fp_merged.join(n)
#             temp = element[1]
#             n.clear()
#             n.append(element[0])
#     song_id = hashlib.sha256(fp_merged.encode()).hexdigest()
#     return song_id,length
#
#
#
#
#
#测试上传
# @app.route('/test/upload')
# def upload_test():
#     return render_template('index.html')
#
# #上传文件
# @app.route('/api/upload',methods = ['POST'],strict_slashes=False)
# def api_upload():
#     file_dir = os.path.join(basedir,app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#
#     f = request.files['song_info'] #从表单的file字段获取文件，song_info为该表单的name值
#     song_name = request.form.get('song_name')
#     musician = request.form.get('musician')
#
#     #print(song_name,musician)
#     if f and valid_file(f.filename):
#         ext = f.filename.rsplit('.',1)[1]
#         unix_time = int(time.time())
#         new_filename = str(unix_time)+'.'+ext
#         token = new_filename.encode()
#         f.save(os.path.join(file_dir, new_filename))
#         #FP(os.path.join(file_dir, new_filename))
#         print(token)
#
#         return jsonify({
#             "error":0,
#             "message":"upload success!",
#             "song_name":song_name,
#             "musician":musician,
#             "token":token
#         })
#     else:
#         return jsonify({
#             "error":1,
#             "message":"upload failed!"
#         })
# if __name__ =='__main__':
#     app.config['JSON_AS_ASCII'] = False
#     app.run(host ='0.0.0.0', port = 5000, debug=True)
app = Flask(__name__)
@app.route('/')
def index():
    ip = request.remote_addr
    return ip

if __name__ =='__main__':
    app.run(host="192.168.0.4",port = 50)

# def get_song_id(song):
#     l = list(song.fingerprints)
#     l = sorted(l, key=lambda x: x[1])
#     length = len(l)
#     fp_merged = ''
#     temp = l[0][1]
#     for element in l:
#         n = []
#         if element[1] == temp:
#             n.append(element[0])
#         else:
#             n = sorted(n, key=lambda x: x)
#             fp_merged.join(n)
#             temp = element[1]
#             n.clear()
#             n.append(element[0])
#
#     print(fp_merged)
#     return hashlib.sha256(fp_merged.encode()).hexdigest(),length

#if __name__ == '__main__':


    # song = Model.Audio.initFromFile('G:/PycharmProjects/CSdissertation/Blockchain/upload/101.flac')
    # song.read()
    # song.getFingerprints()
    #
    # l = list(song.fingerprints)
    # l = sorted(l, key=lambda x: x[1])
    # length = len(l)
    # fp_merged = ''
    # temp = l[0][1]
    # n = []
    # for element in l:
    #     if element[1] == temp:
    #         n.append(element[0])
    #     else:
    #         n = sorted(n, key=lambda x: x)
    #         fp_merged = fp_merged.join(n[0])
    #
    #         temp = element[1]
    #         n.clear()
    #         n.append(element[0])
    #
    # print(fp_merged)

    # song2 = Model.Audio.initFromFile('G:/PycharmProjects/CSdissertation/Blockchain/upload/1583898151.flac')
    # song2.read()
    # song2.getFingerprints()
    #
    # id2, l2 = get_song_id(song2)



# song.getId(new=True)
# print(song.id)
#
# #song.isFingerprinted()
# song.startInsertFingerprints()
