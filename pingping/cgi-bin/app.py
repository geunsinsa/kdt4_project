from flask import Flask, request, render_template, jsonify
import os
from keras.models import load_model
import numpy as np
from PIL import Image
model = load_model('augtotal_VGG19_Dense_add2_lr_0.009_batch_256.hdf5')
yearLabel = {0:'1990',
             1:'2000',
             2:'2010'}

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# # 업로드된 파일을 저장할 디렉토리 설정
# UPLOAD_FOLDER = os.path.join(os.getcwd(), './templates/uploads')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', result_message="아직 없음",internal_script="")

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': '파일을 선택하지 않았습니다.'})

    if file:
        filename = os.path.join("static/upload/uploaded_image.png")
        file.save(filename)


        def imgresize(imgPath, size):
            img = Image.open(imgPath)
            img = img.resize(size)
            img = np.array(img) / 255.0
            return img.reshape((-1, 48, 48, 3))

        img = imgresize("static/upload/uploaded_image.png",(48,48))
        pred = yearLabel[np.argmax(model.predict(img))]
        #여기다가 인공지능 처리하실거 넣으시고




        # 'uploaded_image' 변수를 템플릿에 전달
        return render_template('index.html',  result_message=f"{pred}"
                               ,internal_script="showResult();")

if __name__ == '__main__':
    app.run(debug=True)