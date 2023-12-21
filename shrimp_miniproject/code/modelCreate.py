# 리뷰 데이터로 SimpleRNN 모델 생성해서 저장하는 파일

import pandas as pd
import pickle
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import numpy as np
from keras.models import Sequential
from keras.layers import Embedding, Dense, SimpleRNN, LSTM
from keras.callbacks import ModelCheckpoint
from keras.models import load_model


df = pd.read_csv('../data/reviewDF.csv').drop(columns='Unnamed: 0')
preTextList = []
for i in range(len(df)):
    preTextList.append(df.iloc[i,0])

tokenizer = Tokenizer()
tokenizer.fit_on_texts(preTextList)

file_path = '../models/tokenizer.pkl'
file = open(file_path,'wb')
pickle.dump(tokenizer,file)
file.close()

vocab_size = len(tokenizer.word_index) + 1
sequences = list()
for text in preTextList: # 줄바꿈 문자를 기준으로 문장 토큰화
    encoded = tokenizer.texts_to_sequences([text])[0]
    for i in range(1, len(encoded)):
        sequence = encoded[:i+1]
        sequences.append(sequence)

max_len = 80
sequences = pad_sequences(sequences, maxlen=max_len, padding='pre')
sequences = np.array(sequences)
X = sequences[:,:-1]
y = sequences[:,-1]
y = to_categorical(y, num_classes=vocab_size)

file_path = '../models/one_hot_encoding.pkl'
file = open(file_path,'wb')
pickle.dump(y,file)
file.close()

embedding_dim = 500
hidden_units = 32

mc = ModelCheckpoint(filepath='../models/review.hdf5', monitor='loss', verbose=1, save_best_only=True)

model = Sequential()
model.add(Embedding(vocab_size, embedding_dim))
model.add(SimpleRNN(hidden_units))
model.add(Dense(vocab_size, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(X, y, epochs=1000,batch_size=1024,callbacks=[mc])


