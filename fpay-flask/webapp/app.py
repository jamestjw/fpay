import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

from PIL import Image
import numpy as np
import pandas as pd
import os
from scipy.spatial import KDTree

from openface import *

from models import db, User
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
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            im_array = np.array(Image.open(image))[:,:,:3]
            embedding = get_embeddings(im_array)
            to_append = pd.DataFrame([[request.form['user_name'],request.form['phone']]+[v for v in embedding]],columns=['name','phone']+[str(i) for i in range(128)])
            
            try:
                data_df = pd.read_csv('data.csv')
            except:
                data_df = pd.DataFrame([['dummy_name','dummy_phone']+list(np.random.randn(128))],columns=['name','phone']+[str(i) for i in range(128)])              
            data_df = data_df.append(to_append,sort=False)
            data_df.to_csv('data.csv',index=False)
            return redirect(url_for('success'))
    return render_template("register.html")


@app.route('/identify', methods=["GET", "POST"])
def identify():
    if request.method == "POST":
        if request.files:
            image = np.array(Image.open(request.files['image_blob']))
            try:
                embedding = get_embeddings(image)
                data_df = pd.read_csv('data.csv')
                names = data_df['name'].tolist()
                all_embeddings = data_df.iloc[:,2:].values
                tree = KDTree(all_embeddings)
                dist,idx = tree.query(embedding,k=1)
                if dist < 0.9210277973000384:
                    name = names[idx]
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
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT')))