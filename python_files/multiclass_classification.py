# -*- coding: utf-8 -*-
"""Multiclass_Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nO9EzqkfnD9cBZuwPmF8s9RWVjd69EB-

# Flowers classification with ```Iris dataset```

Where regression was used to predict a numeric value, classification is used to seperate data points into classes of different labels.

```We predict the probability of a flower to belong to that class.```

we have :

```Binary classification or Multiclass classification```

and approaches are:
```
1. Logistic Regression (softmax function)
2. LDA
3. SVM
```

# Setup and Import
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x
from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""# Data load and pre-process

Iris dataset seperates flowers into 3 different classes of species.
- Setosa
- Versicolor
- Virginica

The information about each flower is the following.
- sepal length
- sepal width
- petal length
- petal width
"""

features_col = ['SepalLength', 'SepalWidth', 'PetalLenght', 'PetalWidth', 'Species']
species = ['Setosa', 'Versicolor','Virginica']

# class 0 = 'Setosa'
# class 1 = 'Versicolor'
# class 2 = 'Virginica'

# load dataset using Keras: use keras (a module inside of TensorFlow) to grab our datasets and read them into a pandas dataframe
# tf.keras.utils.get_file(save_file, data_path_from_where_data_will_be_downloaded)

train_path = tf.keras.utils.get_file("iris_training.csv", "https://storage.googleapis.com/download.tensorflow.org/data/iris_training.csv")

test_path = tf.keras.utils.get_file("iris_test.csv", "https://storage.googleapis.com/download.tensorflow.org/data/iris_test.csv")

train_data = pd.read_csv(train_path, names = features_col, header=0) # header 0 , means row 0 is the header
test_data = pd.read_csv(test_path, names = features_col, header=0)

train_data.head()

print(train_data.columns)
print(train_data.shape)

# pop up last column to make it label for tarining

y_train = train_data.pop('Species')
y_test = test_data.pop('Species')

y_train.shape

# now check train_data shape
train_data.shape

"""# Input function


"""

def input_fn(features, labels, training=True, batch_size=256):
    # Convert the Features/inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle and repeat if you are in training mode.
    if training: # if training= True
        dataset = dataset.shuffle(1000).repeat() # shuffle and repeat 1000 times
    
    return dataset.batch(batch_size)

"""# Feature Columns

"""

# Feature columns describe how to use the input/features from input function.

feature_cols = []
for key in train_data.keys(): # train_data.keys : gives all the dataset columns (after y_train removed)
    feature_cols.append(tf.feature_column.numeric_column(key=key))

print(feature_cols)

"""# Create Model 

- can choose either DNN(Deep Neural Network) os LinearClassifier
- DNN can give the best results 
"""

# Build a DNN with 2 hidden layers with 30 and 10 hidden nodes(neurons) each.

# tf.estimator: load bunch of pre-trained models and DNN Classifier is one of them

dnn_classifier= tf.estimator.DNNClassifier(feature_columns = feature_cols,
                                           # Two hidden layers of 30, 10 hidden nodes respectively (for 3 hidden layer use[30,10,10])
                                           hidden_units = [30, 10],
                                           # model has 3 classes
                                           n_classes = 3)


# note
'''
Hidden neurons/Nodes is an arbitrary number and many experiments and tests are usually done to determine the best choice for these values. 
Try playing around with the number of hidden neurons and see if your results change.
'''

"""## Train the Model on training dataset"""

# passing values into input_fn(features = train_data, labels = y_train, training=True, batch_size=256):

dnn_classifier.train(input_fn= lambda: input_fn(train_data, y_train, training=True), steps = 5000) # steps = epoch, batch_size did not pass here(mean it will take default value 256 from input_fn)

# steps argument. This simply tells the classifier to run for 5000 steps. Try modifiying this and seeing if your results change. Keep in mind that more is not always better.
# We include a lambda to avoid creating an inner function inside a function( in logistic regression we had to do that, check it)

"""# Model Evaluation on test dataset"""

evaluation = dnn_classifier.evaluate(input_fn= lambda: input_fn(test_data, y_test, training=False))
print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**evaluation))

"""# Prediciton for new dataset

- user will end features value, and model will predict which class it belongs to
"""

# creating a input function to convert Features into Dataset
# convert features.inputs to a dataset without labels

def input_func(features, batch_size=256): # remeber we are not giving label here because while predicitng value, we dont have label--> we want the label (that is our task)
        return tf.data.Dataset.from_tensor_slices(dict(features)).batch(batch_size) ## it will return a dict

# defining all the featurs into a list
features = ['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth']

### going to take input from user as a list (becase feature value are stores as a list) and convert it into a dict for input_func
predict= {}
print('Please type numeric value as promped: ')
# the coming code to take input from user and validate it if it's in a right type 
for i in features:
  valid = True
  while valid:
    value = input(i + ": ")
    if not value.isdigit(): valid = False ## if entered user input is not digit, validation fails

  predict[i] = [float(value)] ## predict[i] --i = key and [float] --> a list because feature_col is a list and expect all value inside a list 


prediciton = dnn_classifier.predict(input_func=lambda:input_func(predict))  
for pred_dict in prediciton:
  class_id = pred_dict['class_ids'][0]
  prob = pred_dict['probabilities'][class_id]

  print('Prediction is "{}"  (:.1f%)'.format(species[class_id], 100*prob))

# some example input and expected classes you can try above
expected = ['Setosa', 'Versicolor', 'Virginica']
predict_x = {
    'SepalLength': [5.1, 5.9, 6.9],
    'SepalWidth': [3.3, 3.0, 3.1],
    'PetalLength': [1.7, 4.2, 5.4],
    'PetalWidth': [0.5, 1.5, 2.1],
}









