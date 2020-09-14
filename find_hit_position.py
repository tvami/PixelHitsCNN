#============================
# Author: Sanjana Sekhar
# Date: 13 Sep 20
#============================

import h5py
from keras.models import Model
from keras.optimizers import Adam
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras.layers import Flatten
from keras.layers import Input
import tensorflow as tf
from keras.callbacks import ModelCheckpoint
import pylab
from sklearn.metrics import r2_score
import numpy as np

n_train = 41000
n_test = 3000

# Load data
f = h5py.File('train_d49301_d49341.hdf5', 'r')
input_train_1 = f['train_hits'][...]
label_train_1 = f['x'][...]
f.close()
f = h5py.File('test_d49350.hdf5', 'r')
input_test_1 = f['test_hits'][...]
label_test_1 = f['x'][...]
f.close()

input_train = np.zeros((n_train,13,21,1))
label_train = np.zeros((n_train,1))
#shuffle the training arrays -> FIND MORE EFFICIENT WAY TO DO THIS
#create subset
j=0
for i in range(0,41):
	input_train[1000*i:1000*(i+1)]=input_train_1[j:1000+j]
	label_train[1000*i:1000*(i+1)]=label_train_1[j:1000+j]
	j+=30000

input_test = input_test_1[0:n_test]
label_test = label_test_1[0:n_test]

# Model configuration
batch_size = 32
loss_function = 'mean_squared_error'
n_epochs = 5
optimizer = Adam(lr=0.001)
validation_split = 0.2
verbosity = 1
        
#Conv2D -> BatchNormalization -> Pooling -> Dropout

inputs = Input(shape=(13,21,1))
x = Conv2D(16, (3, 3), padding="same")(inputs)
x = Activation("relu")(x)
x = BatchNormalization(axis=-1)(x)
x = MaxPooling2D(pool_size=(3, 3))(x)
x = Dropout(0.25)(x)
x = Conv2D(32, (3, 3), padding="same")(x)
x = Activation("relu")(x)
x = BatchNormalization(axis=-1)(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Dropout(0.25)(x)
x = Conv2D(32, (3, 3), padding="same")(x)
x = Activation("relu")(x)
x = BatchNormalization(axis=-1)(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Dropout(0.25)(x)
x = Flatten()(x)
x = Dense(128)(x)
x = Activation("relu")(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
x = Dense(1)(x)
x_position = Activation("linear", name="x_position")(x)

model = Model(inputs=inputs,
              outputs=x_position
              )

# Display a model summary
model.summary()

# Compile the model
model.compile(loss=loss_function,
              optimizer=optimizer,
              metrics=['mse']
              )

callbacks = [
    ModelCheckpoint("./model_checkpoint", monitor='val_loss')
]

# Fit data to model
history = model.fit(input_train, label_train,
            batch_size=batch_size,
            epochs=n_epochs,
            callbacks=callbacks,
            verbose=verbosity,
            validation_split=validation_split)

# Generate generalization metrics
results = model.evaluate(input_test, label_test, batch_size=32)
print("test loss, test acc:", results)


pylab.plot(history.history['loss'])
pylab.plot(history.history['val_loss'])
pylab.title('model loss')
pylab.ylabel('loss')
pylab.xlabel('epoch')
pylab.legend(['train', 'validation'], loc='upper left')
pylab.show()
pylab.savefig("pixelcnn_x.png")
pylab.close()