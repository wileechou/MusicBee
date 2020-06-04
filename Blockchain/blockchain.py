import hashlib
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from Blockchain.srModule import Model

import json

import requests
from flask import Flask,render_template,jsonify,request
import os
from argparse import ArgumentParser
# {
#     "index": 0,
#     "timestamp": "",
#     "copyright": [
#         {
#             "song_id":"",
#             "song_name":"",
#             "musician":""
#         }
#     ],
#     "proof":"",
#     "previous_hash":"",
# }
class Blockchain:

    def __init__(self):
        self.chain = []
        self.current_copyright = []
        self.nodes = set()


        self.new_block(proof = 1129, previous_hash = 1)

    def register_node(self, address: str):
        # http://127.0.0.1:5000
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self,chain) -> bool:
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash']!=self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes

        max_length = len(self.chain)
        new_chain = None

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False




    def new_block(self, proof, previous_hash = None):

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'copyrights': self.current_copyright,
            'proof': proof,
            'previous_hash':previous_hash or self.hash(self.last_block)
        }

        self.current_copyright = []
        self.chain.append(block)

        return block

    def new_copyright(self,song_id,song_name, musician):
        self.current_copyright.append(
            {
                'song_id':song_id,
                'song_name':song_name,
                'musician': musician
            }
        )
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof : int) -> int:
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof +=1

        #print(proof)
        return proof

    def valid_proof(self, last_proof: int, proof: int) -> bool:
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        #print(guess_hash)
        return guess_hash[0:4] == '0000'


app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['mp3','flac','wma'])

def valid_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def get_songid(filename):
    song = Model.Audio.initFromFile(filename)
    song.read()
    l = list(song.getFingerprints())
    l = sorted(l,key=lambda x:x[1])
    length = len(l)
    fp_merged = ''
    temp = l[0][1]
    for element in l:
        n = []
        if element[1] == temp:
            n.append(element[0])
        else:
            n = sorted(n, key=lambda x: x)
            fp_merged.join(n)
            temp = element[1]
            n.clear()
            n.append(element[0])
    song_id = hashlib.sha256(fp_merged.encode()).hexdigest()
    return song_id,length

blockchain = Blockchain()

node_identifier = str(uuid4()).replace('-','')


@app.route('/home')
def upload_test():
    return render_template('index.html')


# 上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    f = request.files['song_info']  # 从表单的file字段获取文件，song_info为该表单的name值
    song_name = request.form.get('song_name')
    musician = request.form.get('musician')

    # print(song_name,musician)
    if f and valid_file(f.filename):
        ext = f.filename.rsplit('.', 1)[1]
        unix_time = int(time())
        new_filename = str(unix_time) + '.' + ext
        token = new_filename.encode()
        f.save(os.path.join(file_dir, new_filename))
        # FP(os.path.join(file_dir, new_filename))
        print(token)

        song = Model.Audio.initFromFile(os.path.join(file_dir, new_filename))
        song.read()
        #print(os.path.join(file_dir, new_filename))
        print("start to get fingerprints!")
        song.getFingerprints()
        song_id = Model.AudioDecoder.generateFilehash(os.path.join(file_dir, new_filename))

        print("start to recoginze!")
        pos = song.recognize()
        length = len(list(song.fingerprints))

        print(pos['count'],length)
        if pos['count'] / length > 0.5:
            return jsonify({
                "error": 1,
                "message": "Upload faild! Audio already existed!",
                "song_name": song_name,
                "musician": musician
            })
        else:
            print("start insert into local database")

            song.filename = musician +'-'+ song_name
            song.filehash = song_id

            song.getId(new=True)
            print(song.id)
            song.startInsertFingerprints()
            blockchain.current_copyright.append(
                {
                    'song_id': song_id,
                    'song_name': song_name,
                    'musician': musician
                }
            )
            return jsonify({
                "error":0,
                "message":"Upload success! Waiting for minning!",
                "song_id":song_id,
                "song_name":song_name,
                "musician":musician
            })

    else:
        return jsonify({
            "error": 1,
            "message": "Upload failed! Please check ext of file"
        })


@app.route('/copyrights/new', methods=['POST'])
def new_copyright():
    values = request.get_json()
    required = ["song_id","song_name","musician"]

    if values is None:
        return "Missing values", 400
    if not all(k in values for k in required):
        return "Missing values", 400

    index = blockchain.new_copyright(values['song_id'],
                               values['song_name'],
                               values['musician'])
    response = {"message": f'Copyright will be added to Block {index}'}
    return jsonify(response),201


@app.route('/mine', methods = ['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    # 
    # blockchain.new_copyright(sender = "0",
    #                            recipient=node_identifier,
    #                            amount = 1)

    block = blockchain.new_block(proof, None)

    response = {
        "message": "New Block Forged",
        "index": block['index'],
        "copyrights": block['copyrights'],
        "proof": block['proof'],
        "previous_hash": block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/chain', methods = ['GET'])
def full_chain():
    response = {
        'chain':blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

#{ "nodes" : ["http://127.0.0.2:5000"] }

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    if values is None:
        return "Error: please supply a valid list of nodes", 400

    nodes = values.get("nodes")

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes)
    }

    return jsonify(response),201

@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain" : blockchain.chain
        }
    return jsonify(response), 200


if __name__ =='__main__':

    app.config['JSON_AS_ASCII'] = False
    parser = ArgumentParser()
    parser.add_argument('-p','--port', default=8000 , type=int, help='port to listen to')
    args = parser.parse_args()
    port = args.port
    # -p --port

    app.run(host='0.0.0.0',port= port,debug = True)

#testPow = Blockchain()
#testPow.proof_of_work(1129)




