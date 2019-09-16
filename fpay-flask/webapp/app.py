import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from PIL import Image
import numpy as np
import pandas as pd
import os
from scipy.spatial import KDTree
import io 
import base64

from openface import *

from models import db, User


####POSTGRESQL######
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
conn = psycopg2.connect(database='deqfvate2t7tuh',user='wzgyncgeweodyf',password='f4fbd32efb0fe22b19d77f66f1547eab02d1f1e2c9a4df89816614ad8b3c1696',host='ec2-184-73-232-93.compute-1.amazonaws.com',port='5432')
cur = conn.cursor()
###########  HYPERPARAMETERS  ##################################
#Skip image with more than one face
skipMulti = True
size=96
landmarkIndices = AlignDlib.OUTER_EYES_AND_NOSE

###########  APP  ###############################################

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

POSTGRES = {
    'user': 'postgres',
    'password': 526378,
    'database': 'my_database',
    'host': 'localhost',
    'port': '5432',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(database)s' % POSTGRES
db.init_app(app)

###########  MODEL PATH & INSTANTIATION  #######################

fileDir = '/root/openface'
modelDir = os.path.join(fileDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
face_predictor_path = os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat")
model_path = os.path.join(modelDir, 'openface', 'nn4.small2.v1.t7')

#alignment model
align = AlignDlib(face_predictor_path)
#embedding model
model = TorchNeuralNet(model=model_path)
#############  HELPER FUNCTIONS  ############################
def get_embeddings(rgb, plot=False):
    '''
    Get embeddings for an images.
    '''
    outRgb = align.align(size, rgb, landmarkIndices=landmarkIndices, skipMulti=skipMulti)
    out128 = model.forward(outRgb) 
    if plot:
        plt.imshow(outRgb)
    return out128

def get_similarity(A,B,k=1):
    dots = np.dot(A,B.T)
    l2norms = np.sqrt(((A**2).sum(1)[:,None])*((B**2).sum(1)))
    cosine_similarity = 1 - dots/l2norms
    idxs = np.argsort(cosine_similarity)[0]
    return cosine_similarity[0][idxs[:k]], idxs[:k]

def add_quote(s): return "'"+s+"'"

def insert_query(name,phone,embedding):
    embedding = ','.join(map(lambda x:str(x),embedding))
    insert_query = "insert into users values (default,"
    insert_query += add_quote(request.form['user_name'])+ ',' + add_quote(request.form['phone']) + ','
    insert_query += embedding + ');'
    cur.execute(insert_query)
    conn.commit()
#############################################################
try:
    data_df = pd.read_csv('data.csv')
except:
    data_df = pd.DataFrame([['dummy_name','dummy_phone']+list(np.random.randn(128))],columns=['name','phone']+[i for i in range(128)])
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template("success.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        if request.files or request.form['image']:
            try:
                image = request.files["image"]
                im_array = np.array(Image.open(image))[:,:,:3]
            except:
                image = base64.b64decode(str(request.form["image"]))
                im_array = np.array(Image.open(io.BytesIO(image)))[:,:,:3]
            
            embedding = get_embeddings(im_array)
            to_append = pd.DataFrame([[0,request.form['user_name'],request.form['phone']]+[v for v in embedding]],columns=['id','name','phone']+['v'+str(i) for i in range(128)])
            globals()['data_df'] = data_df.append(to_append,sort=False)
            insert_query(request.form['user_name'],request.form['phone'],embedding)
            return redirect(url_for('success'))
    return render_template("register.html")


@app.route('/identify', methods=["GET", "POST"])
def identify():
    if request.method == "POST":
        if request.files:
            image = np.array(Image.open(request.files['image_blob']))
            try:
                embedding = get_embeddings(image)
                names = data_df['name'].tolist()
                all_embeddings = data_df.iloc[:,3:].values
                dist,idx = get_similarity(embedding[None],all_embeddings,k=1)
                if dist[0] < 0.35:
                    name = names[idx[0]]
                    response = {'name':name}
                    return jsonify(response)
                else:
                    return jsonify()
            except:
                return jsonify()
    return render_template('identify.html')

@app.route('/<name>')
def hello_name(name):
    return "Undefined route: {}!".format(name)

if __name__ == '__main__':
    # globals()['data_df']= pd.read_csv('data.csv')
    globals()['data_df']=sqlio.read_sql_query('Select * from users', conn)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT')))
