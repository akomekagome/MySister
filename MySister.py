# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

pip install awscli

pip install opencv-python

pip install uuid

# +
import tkinter as ttk
import pickle
import uuid
import os

mac_adress = uuid.getnode()
pickle_name = "macadressdict.pickle"

# os.remove(pickle_name)

mac_adress_dict = {}
if os.path.exists(pickle_name) and os.path.getsize(pickle_name) > 0:
    with open(pickle_name, 'rb') as f:
        mac_adress_dict = pickle.load(f)
else:
    with open(pickle_name, "wb") as f:
        pass

path_dict = {} if not mac_adress_dict  else mac_adress_dict[mac_adress] if mac_adress in mac_adress_dict else  mac_adress_dict[0]

root = ttk.Tk()
root.title('Path List')

#入力用フレーム
frame0 = ttk.Frame(root)
frame0.grid(row=0, column=0)

#項目をつくる
path_names = ["cascade_path"]
list_Labels = ["Name", "Path"]

n = len(path_names)
for i in range(0, len(list_Labels)):
    label0 = ttk.Label(frame0,
                       text=list_Labels[i])
    label0.grid(row=0, column=i)

#項目1　リストから選ぶ
list_Items1 = [0] * n
for i in range(0, n):  
    list_Items1[i] = ttk.Label(frame0,text=path_names[i],width=20)
    list_Items1[i].grid(row=i+1, column=0)
    
#項目2　手入力する
list_Items2 = [0] * n
for i in range(0, n):
    list_Items2[i] = ttk.StringVar()
    path_name = path_names[i]
    if path_name in path_dict:
        list_Items2[i].set(path_dict[path_name])
    entry_Item2 = ttk.Entry(frame0,
                            textvariable=list_Items2[i],
                            width=20)
    entry_Item2.grid(row=i+1,column=1)
    
root.mainloop()

buffer = dict(zip(path_names, [item2.get() for item2 in list_Items2]))
mac_adress_dict[mac_adress]= buffer;

with open(pickle_name, "wb") as f:
    pickle.dump(mac_adress_dict, f)


# -

class _const:
    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        if name in self.__dict__.keys():
            raise self.ConstError('readonly。再代入禁止。')
        self.__dict__[name]=value


# +
const_ins = _const()

with open(pickle_name, 'rb') as f:
    mac_adress_dict = pickle.load(f)
const_ins.path_dict = mac_adress_dict[mac_adress]

# +
import tkinter as tk
import tkinter.filedialog as tkdialog
import platform
import os

system = platform.system()
fname = None
if system == "Darwin":
    fTyp=[('png files','*.png'), ('jpeg files','*.jpeg')]
    root  = tk.Tk()
    root.withdraw()
    fname = tkdialog.askopenfilename(filetypes=fTyp,initialdir=os.getcwd())
    root.update()
    root.destroy()
elif system == "Windows":
    print("windows")

# +
import boto3

collation_image_path = "Test/akome1.jpeg"
collation_bucket_path  = "akomekagome.example.img"

# print(fname)
with open(fname, 'rb') as f:
    imageBody = f.read()

s3=boto3.resource('s3')
bucket=s3.Bucket(collation_bucket_path)
bucket.put_object(
    Body=imageBody,
    Key=collation_image_path
)

# +
import boto3

collection_id='FaceCollection'

client = boto3.client('rekognition', region_name="ap-northeast-1")
collections = client.list_collections()
if not collection_id in collections['CollectionIds']:
    client.create_collection(CollectionId=collection_id)
response=client.index_faces
response=client.index_faces(CollectionId=collection_id,Image={'S3Object':{'Bucket':collation_bucket_path,'Name':collation_image_path}})

# +
import boto3

def authenticate_face(standard_value,collectionId, bucket_path, path):
    rek_res = client.search_faces_by_image(CollectionId = collectionId, Image={'S3Object':{'Bucket':bucket_path,'Name':path}})
    similarity  =rek_res['FaceMatches'][0]['Similarity']
    return similarity > standard_value


# +
import cv2
import boto3

imag_name = "face.jpg"
output_path = "./" + imag_name
cascade_path = const_ins.path_dict['cascade_path']
verification_bucket_path  = "akomekagome.example.mov"
standard_value = 0.95

s3=boto3.resource('s3')
cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cascade_path)
    facerect = cascade.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=2, minSize=(30, 30))
    if len(facerect) > 0:
        cv2.imwrite(output_path, image)
        s3.Bucket(verification_bucket_path).upload_file(output_path,imag_name)
        if(authenticate_face(standard_value, collection_id, verification_bucket_path, imag_name)):
            print("match")
            break
        else:
            print("no match")
            continue
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
os.remove(output_path)
cap.release()
