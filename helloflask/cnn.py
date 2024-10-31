import pandas as pd
import numpy as np
import cv2
import os

from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from keras.models import Sequential, model_from_json
from keras.utils import to_categorical
from os.path import isfile, join
from keras import backend as K
from os import listdir
from PIL import Image
import tensorflow as tf

index_by_directory = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '+': 10,
    '-': 11,
    'x': 12,
    '√': 13
}

def get_index_by_directory(directory):
    return index_by_directory[directory]

def load_images_from_folder(folder):
    train_data = []

    for filename in os.listdir(folder):  # 폴더 내의 파일 리스트
        img = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)  # 그레이스케일로 이미지 읽기
        img = ~img  # 이미지 반전
        if img is not None:
            _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 이진화
            ctrs, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cnt = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])  # x 좌표 기준 정렬
            maxi = 0
            for c in cnt:
                x, y, w, h = cv2.boundingRect(c)
                if w * h > maxi:
                    maxi = w * h
                    x_max = x
                    y_max = y
                    w_max = w
                    h_max = h
            im_crop = thresh[y_max:y_max + h_max + 10, x_max:x_max + w_max + 10]  # 이미지 크롭
            im_resize = cv2.resize(im_crop, (28, 28))  # 이미지 리사이즈
            im_resize = np.reshape(im_resize, (784,))  # 1차원 배열로 변환
            train_data.append(im_resize)
    return train_data

def load_all_imgs():
    dataset_dir = "./datasets/"
    directory_list = listdir(dataset_dir)
    first = True
    data = []

    print('Exporting images...')
    for directory in directory_list:
        print(directory)
        if first:
            first = False
            data = load_images_from_folder(dataset_dir + directory)
            for i in range(len(data)):
                data[i] = np.append(data[i], [str(get_index_by_directory(directory))])
            continue

        aux_data = load_images_from_folder(dataset_dir + directory)
        for i in range(len(aux_data)):
            aux_data[i] = np.append(aux_data[i], [str(get_index_by_directory(directory))])
        data = np.concatenate((data, aux_data))

    df = pd.DataFrame(data, index=None)
    df.to_csv('model/train_data.csv', index=False)

def extract_imgs(img):
    img = ~img  # 이미지 반전
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)  # 이진화
    ctrs, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnt = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])  # x 좌표 기준 정렬

    img_data = []
    rects = []
    for c in cnt:
        x, y, w, h = cv2.boundingRect(c)
        rect = [x, y, w, h]
        rects.append(rect)

    # 충돌하는 사각형을 효율적으로 처리
    final_rects = []
    for rect in rects:
        is_inside = False
        for other_rect in rects:
            if rect == other_rect:
                continue
            x_overlap = rect[0] >= other_rect[0] and (rect[0] + rect[2]) <= (other_rect[0] + other_rect[2])
            y_overlap = rect[1] >= other_rect[1] and (rect[1] + rect[3]) <= (other_rect[1] + other_rect[3])
            if x_overlap and y_overlap:
                is_inside = True
                break
        if not is_inside:
            final_rects.append(rect)

    for r in final_rects:
        x = r[0]
        y = r[1]
        w = r[2]
        h = r[3]

        im_crop = thresh[y:y + h + 10, x:x + w + 10]  # 이미지 크롭
        im_resize = cv2.resize(im_crop, (28, 28))  # 이미지 리사이즈
        im_resize = np.reshape(im_resize, (28, 28, 1))  # 3차원 배열로 변환
        img_data.append(im_resize)

    return img_data

class ConvolutionalNeuralNetwork:
    def __init__(self):
        if os.path.exists('model/model_weights.h5') and os.path.exists('model/model.json'):
            self.load_model()
        else:
            self.create_model()
            self.train_model()
            self.export_model()
        # 예측 함수 캐싱
        self.predict_fn = tf.function(self.model.predict, reduce_retracing=True)

    def load_model(self):
        print('Loading Model...')
        with open('model/model.json', 'r') as model_json_file:
            loaded_model_json = model_json_file.read()
        loaded_model = model_from_json(loaded_model_json)

        print('Loading weights...')
        loaded_model.load_weights("model/model_weights.h5")

        self.model = loaded_model

    def create_model(self):
        first_conv_num_filters = 30
        first_conv_filter_size = 5
        second_conv_num_filters = 15
        second_conv_filter_size = 3
        pool_size = 2

        print("Creating Model...")
        self.model = Sequential()
        self.model.add(Conv2D(first_conv_num_filters, (first_conv_filter_size, first_conv_filter_size),
                              input_shape=(28, 28, 1), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))
        self.model.add(Conv2D(second_conv_num_filters, (second_conv_filter_size, second_conv_filter_size),
                              activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))
        self.model.add(Dropout(0.2))
        self.model.add(Flatten())
        self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(50, activation='relu'))
        self.model.add(Dense(14, activation='softmax'))

        print("Compiling Model...")
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy'],
        )

    def train_model(self):
        if not os.path.exists('model/train_data.csv'):
            load_all_imgs()

        csv_train_data = pd.read_csv('model/train_data.csv', index_col=False)

        y_train = csv_train_data[['784']].astype('int')
        csv_train_data.drop(csv_train_data.columns[[784]], axis=1, inplace=True)

        x_train = csv_train_data.values.reshape(-1, 28, 28, 1)
        y_train = to_categorical(y_train, num_classes=14)

        print('Training model...')
        self.model.fit(
            x_train,
            y_train,
            epochs=10,
            batch_size=200,
            shuffle=True,
            verbose=1
        )

    def export_model(self):
        model_json = self.model.to_json()
        with open('model/model.json', 'w') as json_file:
            json_file.write(model_json)
        self.model.save_weights('model/model_weights.h5')

    def predict(self, operationBytes):
        Image.open(operationBytes).save('aux.png')
        img = cv2.imread('aux.png', cv2.IMREAD_GRAYSCALE)
        os.remove('aux.png')

        if img is not None:
            img_data = extract_imgs(img)
            operation = ''

            # 각 이미지에 대해 예측 수행
            for img in img_data:
                img = img.reshape(-1, 28, 28, 1)

                # Model.predict 대신 모델을 직접 호출
                predictions = self.model(img)  # 이 부분을 변경
                result = np.argmax(predictions, axis=-1)[0]

                # 결과를 문자열로 변환
                operation += {10: '+', 11: '-', 12: 'x', 13: '√'}.get(result, str(result))

            return operation

    
