from keras.models import load_model
import pickle
import numpy as np
from keras.preprocessing.sequence import pad_sequences

model = load_model('../models/review.hdf5')
tokenizer = pickle.load(open('../models/tokenizer.pkl', 'rb'))
# ohc = pickle.load(open('../models/one_hot_encoding.pkl', 'rb'))

# # 문장을 넣으면 다음 단어를 추천 3개를 보여주는 함수
# def sentence_generation(model, tokenizer, current_word): # 모델, 토크나이저, 현재 단어, 반복할 횟수
#     init_word = current_word
#     sentence = ''
#
#
#     # 현재 단어에 대한 정수 인코딩과 패딩
#     encoded = tokenizer.texts_to_sequences([current_word])[0]
#     encoded = pad_sequences([encoded], maxlen=80, padding='pre')
#
#     # 입력한 X(현재 단어)에 대해서 Y를 예측하고 Y(예측한 단어)를 result에 저장.
#     # 입력한 X(현재 단어)에 대해서 Y를 예측하고 Y(예측한 단어)를 result에 저장.
#     result = model.predict(encoded)
#     sorted_indices = np.argsort(result)
#
#     low3_index = sorted_indices[0,[-1,-2,-3]]
#
#
#     resultTop3 = []
#     for idx in low3_index:
#         for word, index in tokenizer.word_index.items():
#
#             if index == idx:
#                 resultTop3.append([word,result[0,idx]])
#                 break
#
#     return resultTop3[0],resultTop3[1], resultTop3[2]
#
# current_word = input('리뷰에 쓸 첫번째 단어를 입력해주세요 : ')
# Flag = True
# while Flag:
#     print(f"현재 완성된 리뷰 문장 : {current_word}")
#     print("-----------------------------------")
#     result = sentence_generation(model, tokenizer,current_word)
#     for i in range(len(result)):
#         print(f"{i+1}번째 -> 단어 : {result[i][0]}, 확률 : {result[i][1]}")
#     print('-----------------------------------')
#
#     next_word = input('다음 단어를 선택해주세요 : ').strip()
#     if next_word in ['q','Q']:
#         print('-----------------------------------')
#         print(f"완성된 문장 : {current_word}")
#         Flag = False
#     else:
#         current_word = current_word + ' ' + next_word












# 키워드와 단어개수(n)를 정해주면 문장을 자동으로 만들어주는 함수
def sentence_generation(model, tokenizer, current_word, n, max_len):
    if n == 0:
        return [current_word]  # Base case: When the desired word count is 0, return the current word as a list.

    sentences = []

    # Encodes the current word
    encoded = tokenizer.texts_to_sequences([current_word])[0]
    encoded = pad_sequences([encoded], maxlen=max_len, padding='pre')

    # Predict the next word
    result = model.predict(encoded)
    sorted_indices = np.argsort(result)

    low3_index = sorted_indices[0, [-1, -2,-3]]

    resultTop3 = []
    for idx in low3_index:
        for word, index in tokenizer.word_index.items():
            if index == idx:
                resultTop3.append(word)
                break

    # Recursively generate sentences for the next word
    for next_word in resultTop3:
        next_sentences = sentence_generation(model, tokenizer, next_word, n - 1, max_len)
        for sentence in next_sentences:
            sentences.append(current_word + ' ' + sentence)

    return sentences

Flag = True
while Flag:
    keyword, length  = input('키워드 및 단어 개수를 입력해주세요(ex 바지 5) : ').strip().split()
    if keyword in ['q','Q']:
        Flag = False
    else:
        resulting_sentences = sentence_generation(model, tokenizer, keyword, int(length), 1000)
        for sentence in resulting_sentences:
            print(sentence)

