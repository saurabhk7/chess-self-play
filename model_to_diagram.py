from keras.utils import plot_model

import sys
sys.path.append('..')
from utils import *

import argparse
from keras.models import *
from keras.layers import *
from keras.optimizers import *


# game params
board_x = 8
board_y = 8 
action_size = 64*64
#args = args

# Neural Net
input_boards = Input(shape=(board_x, board_y))    # s: batch_size x board_x x board_y

x_image = Reshape((board_x, board_y, 1))(input_boards)                # batch_size  x board_x x board_y x 1
h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(512, 3, padding='same')(x_image)))         # batch_size  x board_x x board_y x num_channels
h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(512, 3, padding='same')(h_conv1)))         # batch_size  x board_x x board_y x num_channels
h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(512, 3, padding='valid')(h_conv2)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(512, 3, padding='valid')(h_conv3)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
h_conv5 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(512, 3, padding='valid')(h_conv4)))        # batch_size  x (board_x-6) x (board_y-6) x num_channels
h_conv5_flat = Flatten()(h_conv5)       
s_fc1 = Dropout(0.3)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024)(h_conv5_flat))))  # batch_size x 1024
s_fc2 = Dropout(0.3)(Activation('relu')(BatchNormalization(axis=1)(Dense(512)(s_fc1))))          # batch_size x 1024
pi = Dense(action_size, activation='softmax', name='pi')(s_fc2)   # batch_size x action_size
v = Dense(1, activation='tanh', name='v')(s_fc2)                    # batch_size x 1

model = Model(inputs=input_boards, outputs=[pi, v])
model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(0.001))


plot_model(model, to_file='model.png', show_shapes=True)
