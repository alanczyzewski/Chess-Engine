import numpy as np
import chess
import os
from tensorflow.keras import callbacks, optimizers
from tensorflow.keras.layers import (LSTM, BatchNormalization, Dense, Dropout, Flatten,
                          TimeDistributed, Conv2D, MaxPooling2D, Embedding, Input, Reshape, Activation, GlobalMaxPooling2D, Concatenate, Add)
from tensorflow.keras.models import Sequential, load_model, model_from_json
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.initializers import HeNormal
from tensorflow.keras.regularizers import l1_l2
from tensorflow.keras import Model
from sklearn.model_selection import train_test_split
import pickle
import tensorflow as tf

# def get_model():
#     base_l1 = 3e-4
#     base_l2 = 3e-4
#     accum = [42]
#
#     def get_seed():
#         accum[0] += 1
#         return accum[0]
#     def conv_layer(prev_layer, filters, kernel_size, padding='valid'):
#         conv = Conv2D(filters=filters, kernel_size=kernel_size, padding=padding, activation='linear',
#                kernel_initializer=HeNormal(seed=get_seed()),
#                kernel_regularizer=l1_l2(base_l1, base_l2), bias_regularizer=l1_l2(base_l1, base_l2))(prev_layer)
#         bn = BatchNormalization()(conv)
#         relu = Activation('relu')(bn)
#         return relu
#     def dense_layer(prev_layer, neurons, activation='linear'):
#         densee = Dense(neurons, activation='linear', kernel_initializer=HeNormal(seed=get_seed()),
#                         kernel_regularizer=l1_l2(base_l1 * 2, base_l2 * 2), bias_regularizer=l1_l2(base_l1, base_l2))(prev_layer)
#         ret = BatchNormalization()(densee)
#         if activation!= 'linear':
#             act = Activation(activation)(ret)
#             return act
#         return ret
#     def inception_block(prev_layer, filters_base, filters_base2):
#         conv_1x1_3 = conv_layer(prev_layer, filters_base*4, 1, padding='same')
#         conv_1x1_5 = conv_layer(prev_layer, filters_base*2, 1, padding='same')
#         conv_1x1_7 = conv_layer(prev_layer, filters_base, 1, padding='same')
#
#         # conv_1x1_1 = conv_layer(prev_layer, filters_base*3, 1, padding='same')
#         # conv_1x1 = conv_layer(conv_1x1_1, filters_base2*5, 1, padding='same')
#         21 * filters_base * filters_base2
#         conv_3x3 = conv_layer(conv_1x1_3, filters_base2*4, 3, padding='same')
#         conv_5x5 = conv_layer(conv_1x1_5, filters_base2*2, 5, padding='same')
#         conv_7x7 = conv_layer(conv_1x1_7, filters_base2, 7, padding='same')
#
#         concat_1 = Concatenate(-1)([conv_3x3, conv_5x5])
#         return concat_1
#
#     inp = Input(shape=(8,8))
#     rshp1 = Reshape((64,))(inp)
#     embed = Embedding(14, 9, input_length=64)(rshp1)
#     rshp2 = Reshape((8, 8, 9))(embed)
#
#
#
#
#     inception1 = inception_block(rshp2, 8, 16)
#     inception2 = inception_block(inception1, 8, 16)
#     # inception3 = inception_block(inception2, 8, 16)
#     # inception4 = inception_block(inception3, 8, 16)
#
#     conv_1x1_1 = conv_layer(inception2, 32, 1)
#
#     pooling_output_4x4 = MaxPooling2D()(conv_1x1_1)
#
#     conv_3x3_1 = conv_layer(pooling_output_4x4, 64, 3, padding='same')
#     conv_3x3_output_2x2 = conv_layer(conv_3x3_1, 64, 3, padding='valid')
#
#     gmp = GlobalMaxPooling2D()(conv_3x3_output_2x2)
#
#     flat = Flatten()(gmp)
#
#     dense_1 = dense_layer(flat, 32, 'relu')
#     out = dense_layer(dense_1, 1)
#
#     model = Model(inputs=inp, outputs=out)
#     model.compile(optimizer=Adam(learning_rate=2e-4), loss='logcosh', metrics=['mse', 'mae'])
#     model.summary()
#     return model


def get_model():
    base_l1 = 3e-4
    base_l2 = 3e-4
    accum = [42]

    def get_seed():
        accum[0] += 1
        return accum[0]
    def conv_layer(prev_layer, filters, kernel_size, padding='valid'):
        conv = Conv2D(filters=filters, kernel_size=kernel_size, padding=padding, activation='linear',
               kernel_initializer=HeNormal(seed=get_seed()),
               kernel_regularizer=l1_l2(base_l1, base_l2), bias_regularizer=l1_l2(base_l1, base_l2))(prev_layer)
        bn = BatchNormalization()(conv)
        relu = Activation('relu')(bn)
        return relu
    def dense_layer(prev_layer, neurons, activation='linear'):
        densee = Dense(neurons, activation='linear', kernel_initializer=HeNormal(seed=get_seed()),
                        kernel_regularizer=l1_l2(base_l1 * 2, base_l2 * 2), bias_regularizer=l1_l2(base_l1, base_l2))(prev_layer)
        ret = BatchNormalization()(densee)
        if activation!= 'linear':
            act = Activation(activation)(ret)
            return act
        return ret
    def inception_block(prev_layer, filters_base, filters_base2):
        conv_1x1_3 = conv_layer(prev_layer, filters_base*4, 1, padding='same')
        conv_1x1_5 = conv_layer(prev_layer, filters_base*2, 1, padding='same')
        conv_1x1_7 = conv_layer(prev_layer, filters_base, 1, padding='same')

        # conv_1x1_1 = conv_layer(prev_layer, filters_base*3, 1, padding='same')
        # conv_1x1 = conv_layer(conv_1x1_1, filters_base2*5, 1, padding='same')
        21 * filters_base * filters_base2
        conv_3x3 = conv_layer(conv_1x1_3, filters_base2*4, 3, padding='same')
        conv_5x5 = conv_layer(conv_1x1_5, filters_base2*2, 5, padding='same')
        conv_7x7 = conv_layer(conv_1x1_7, filters_base2, 7, padding='same')

        concat_1 = Concatenate(-1)([conv_3x3, conv_5x5])
        return concat_1

    inp = Input(shape=(8,8))
    rshp1 = Reshape((64,))(inp)
    embed = Embedding(14, 9, input_length=64)(rshp1)
    rshp2 = Reshape((8, 8, 9))(embed)




    inception1 = inception_block(rshp2, 4, 16)
    inception2 = inception_block(inception1, 8, 16)
    # inception3 = inception_block(inception2, 8, 16)
    # res = Add()([inception1, inception2, inception3])
    # inception4 = inception_block(inception3, 8, 16)

    conv_1x1_1 = conv_layer(inception2, 32, 1)

    pooling_output_4x4 = MaxPooling2D()(conv_1x1_1)

    conv_3x3_1 = conv_layer(pooling_output_4x4, 64, 3, padding='same')
    conv_1x1_2 = conv_layer(conv_3x3_1, 32, 1)
    conv_3x3_output_2x2 = conv_layer(conv_1x1_2, 64, 3, padding='valid')

    gmp = GlobalMaxPooling2D()(conv_3x3_output_2x2)

    flat = Flatten()(gmp)

    # dense_1 = dense_layer(flat, 128, 'relu')
    dense_2 = dense_layer(flat, 32, 'relu')

    out = dense_layer(dense_2, 1, activation='tanh')

    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer=Adam(learning_rate=2e-4), loss='logcosh', metrics=['mse', 'mae'])
    model.summary()
    return model
if __name__ == '__main__':
    with open('data.pickle', 'rb') as f:
        data = pickle.load(f)
    with open('labels.pickle', 'rb') as f:
        labels = pickle.load(f)
    # np.random.shuffle(labels)
    data = np.where(np.sum(data, axis=-1) != 0, np.argmax(data, axis=-1) + 1, 0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, random_state=42)
    model = get_model()
    model.load_weights('tempw2')
    callback = tf.keras.callbacks.EarlyStopping(monitor='val_mse', patience=10, restore_best_weights=True)
    callback2 = tf.keras.callbacks.ModelCheckpoint(
    'tempw3', monitor='val_mse', verbose=0, save_best_only=True,
    save_weights_only=True)
    model.fit(X_train, y_train, batch_size=1024, epochs=50, verbose=1, callbacks=[callback, callback2], validation_data=(X_test, y_test), shuffle=True, use_multiprocessing=True, workers=6)
    model.save_weights('model2.weights')

    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    import matplotlib.pyplot as plt
    def hist(jojo_pret, jojo_sru, lim=1.2 ):
        # plt.subplots(1,2)
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(5, 3), sharey=True)

        axes[0].hist(jojo_pret, bins=200)

        axes[1].hist(jojo_sru, bins=200)
        axes[0].set_xlim((-lim, lim))
        axes[1].set_xlim((-lim, lim))

        plt.yscale('log')
        plt.show()

    def scatter(tru, error):
        plt.scatter(tru, error, s=1)
        plt.show()

    hist(pred_train, y_train)
    hist(pred_test, y_test)

    error_train = np.squeeze(pred_train) - y_train
    error_test = np.squeeze(pred_test) - y_test
    hist(error_train, error_test, lim=2.2)
    scatter(y_train, error_train)
    scatter(y_test, error_test)


