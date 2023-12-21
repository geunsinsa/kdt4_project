from keras.models import load_model
import pickle
import numpy as np
from keras.preprocessing.sequence import pad_sequences

model = load_model('./ModelList/g/review.hdf5')
tokenizer = pickle.load(open('./ModelList/g/tokenizer.pkl','rb'))
#ohc = pickle.load(open('./ModelList/g/one_hot_encoding.pkl','rb'))

def sentence_generation(current_word):
    init_word = current_word
    sentence = ''


    # 현재 단어에 대한 정수 인코딩과 패딩
    encoded = tokenizer.texts_to_sequences([current_word])[0]
    encoded = pad_sequences([encoded], maxlen=80, padding='pre')

    # 입력한 X(현재 단어)에 대해서 Y를 예측하고 Y(예측한 단어)를 result에 저장.
    # 입력한 X(현재 단어)에 대해서 Y를 예측하고 Y(예측한 단어)를 result에 저장.
    result = model.predict(encoded)
    sorted_indices = np.argsort(result)

    low3_index = sorted_indices[0,[-1,-2,-3]]


    resultTop3 = []
    for idx in low3_index:
        for word, index in tokenizer.word_index.items():

            if index == idx:
                resultTop3.append([word,result[0,idx]])
                break

    return resultTop3[0],resultTop3[1], resultTop3[2]