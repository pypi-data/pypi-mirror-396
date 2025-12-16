import tensorflow as tf
from tensorflow import keras

event_num = 3
droprate = 0.3
def DNN(**params):
    input_shape = params.get('input_shape')
    vector_size = input_shape[0]
    model = keras.Sequential()
    model.add(keras.layers.Input(shape=(vector_size,), name='Inputlayer'))
    model.add(keras.layers.Dense(512, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dropout(droprate))
    model.add(keras.layers.Dense(256, activation='relu'))
    model.add(keras.layers.BatchNormalization())
    model.add(keras.layers.Dropout(droprate))
    model.add(keras.layers.Dense(event_num))
    model.add(keras.layers.Activation('softmax'))
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy', metrics=['accuracy'])
# ['accuracy',metrics.Precision() ]
    return model


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

def create_model(**params):
    print("params:")
    print(params)
    input_shape = params.get('input_shape')

    if len(input_shape) == 1:
      s = 1
    else:
      s = input_shape[1]
    model = Sequential([
        Dense(64, activation='relu', input_shape=(s,)),
        Dense(32, activation='relu'),
        Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model
  
  
def CNN(**params):
    # Set default values or get from params
    input_shape = params.get('input_shape')
    sequence_length = input_shape[1]
    embedding_dim = input_shape[2]
    # sequence_length = params.get('sequence_length', 2)  # default to 2
    # embedding_dim = params.get('embedding_dim', 2048)  # default to 2048
    num_classes = params.get('num_classes', event_num)  # default to 65 classes

    # Ensure parameters are correct types
    if not isinstance(sequence_length, int) or not isinstance(embedding_dim, int) or not isinstance(num_classes, int):
        raise ValueError(
            "sequence_length, embedding_dim, and num_classes must be integers")

    # Create the CNN model
    model = keras.Sequential([
        keras.layers.Input(shape=(sequence_length, embedding_dim)),
        keras.layers.Conv1D(128, 1, activation='relu'),
        # keras.layers.MaxPooling1D(pool_size=1),
        keras.layers.MaxPooling1D(pool_size=1, strides=1),
        keras.layers.Flatten(),
        # keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(num_classes, activation='softmax')
    ])

    # Compile the model
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                #   loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    return model