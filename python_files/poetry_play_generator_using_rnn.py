# -*- coding: utf-8 -*-
"""Poetry_Play_Generator_using_RNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xpUqG3nFmD9BHbd4En-rXQMWlM3iX76B

# RNN Poetry Play Generator

 We are going to use a RNN to generate a play. We will simply show the RNN an example of something we want it to recreate and it will learn how to write a version of it on its own. We'll do this using a character predictive model that will take as input a variable length sequence and predict the next character. We can use the model many times in a row with the output from the last predicition as the input for the next call to generate a sequence.


*This guide is based on the following: https://www.tensorflow.org/tutorials/text/text_generation*

# import and setup
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x  
from keras.preprocessing import sequence
import keras
import tensorflow as tf
import os
import numpy as np

"""# Dataset: from shakesphere play
For this example, we only need one peice of training data. In fact, we can write our own poem or play and pass that to the network for training if we'd like. However, to make things easy we'll use an extract from a shakesphere play.
"""

path_to_file = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')

'''
###Loading Your Own Data
To load your own data, you'll need to upload a file from the dialog below. 
Then you'll need to follow the steps from above but load in this new file instead.

'''

# load the dataset from local computer 
#from google.colab import files
#path_to_file = list(files.upload().keys())[0]

"""### Read Contents of File
Let's look at the contents of the file.
"""

# Read, then decode for py2 compat.
# rb: read byte mode
text = open(path_to_file, 'rb').read().decode(encoding = 'utf-8')


# length of text is the number of characters in it
print ('Length of text: {} characters'.format(len(text)))

# take a look at first 250 characters in the text
print(text[:250])

"""# Encoding
Since this text isn't encoded yet,we will need to do that ourselves. We are going to encode each unique character as a different integer.
"""

vocab = sorted(set(text))
# Creating a mapping from unique characters to indices
char2idx = {u:i for i, u in enumerate(vocab)} # char to int
idx2char = np.array(vocab) # int to char

def text_to_int(text):
  return np.array([char2idx[c] for c in text])

text_as_int = text_to_int(text)

# lets look at how part of our text is encoded
print("Text:", text[:13])
print("Encoded:", text_to_int(text[:13]))

# And here we will make a function that can convert our numeric values to text.

def int_to_text(ints):
  try:
    ints = ints.numpy()
  except:
    pass
  return ''.join(idx2char[ints])

print(int_to_text(text_as_int[:13]))

"""###Creating Training Examples
Remember our task is to feed the model a sequence and have it return to us the next character. This means we need to split our text data from above into many shorter sequences that we can pass to the model as training examples. 

The training examples we will prepapre will use a *seq_length* sequence as input and a *seq_length* sequence as the output where that sequence is the original sequence shifted one letter to the right. For example:

```input: Hell | output: ello```

Our first step will be to create a stream of characters from our text data.
"""

# each sequence length is 100 and we are creating batch_size = 64 means at one time 64 sequences will be pass to model

seq_length = 100  # length of sequence for a training example
examples_per_epoch = len(text)//(seq_length+1)

# Create training examples / targets
char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

# Next we can use the batch method to turn this stream of characters into batches of desired length


sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

# Now we need to use these sequences of length 101 and split them into input 
# and output.

def split_input_target(chunk):  # for the example: hello
    input_text = chunk[:-1]  # hell
    target_text = chunk[1:]  # ello
    return input_text, target_text  # hell, ello

dataset = sequences.map(split_input_target)  # we use map to apply the above function to every entry

for x, y in dataset.take(2):
  print("\n\nEXAMPLE\n")
  print("INPUT")
  print(int_to_text(x))
  print("\nOUTPUT")
  print(int_to_text(y))

# Finally we need to make training batches.


BATCH_SIZE = 64
VOCAB_SIZE = len(vocab)  # vocab is number of unique characters
EMBEDDING_DIM = 256
RNN_UNITS = 1024

# Buffer size to shuffle the dataset
# (TF data is designed to work with possibly infinite sequences,
# so it doesn't attempt to shuffle the entire sequence in memory. Instead,
# it maintains a buffer in which it shuffles elements).
BUFFER_SIZE = 10000

data = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

"""## Building the Model
Now it is time to build the model. We will use an embedding layer a LSTM and one dense layer that contains a node for each unique character in our training data. The dense layer will give us a probability distribution over all nodes.
"""

# while modeul build, batch_size=65 bcz at training time, we will give 64 sequence together
# but at prediciton, we just need batch_size = 1, means 1 sequence as input and 1 sequence as output


def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim,
                              batch_input_shape=[batch_size, None]), # none: dont know how long sequences gonna be in each batch
    tf.keras.layers.LSTM(rnn_units,
                        return_sequences=True, # want to see swquence of all input sequence
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.Dense(vocab_size)
  ])
  return model

model = build_model(VOCAB_SIZE,EMBEDDING_DIM, RNN_UNITS, BATCH_SIZE)
model.summary()


## dense (Dense)--> (64, None, 65) --> we will always get 65 size at output

"""## Creating a Loss Function
Now we are going to create our own loss function for this problem. This is because our model will output a (64, sequence_length, 65) shaped tensor that represents the probability distribution of each character at each timestep for every sequence in the batch. 






However, before we do that let's have a look at a sample input and the output from our untrained model. This is so we can understand what the model is giving us.


"""

for input_example_batch, target_example_batch in data.take(1):
  example_batch_predictions = model(input_example_batch)  # ask our model for a prediction on our first batch of training data (64 entries)
  print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")  # print out the output shape

# we can see that the predicition is an array of 64 arrays, one for each entry in the batch
print(len(example_batch_predictions))
print(example_batch_predictions)

# lets examine one prediction
pred = example_batch_predictions[0]
print(len(pred))
print(pred)
# notice this is a 2d array of length 100, where each interior array is the prediction for the next character at each time step

# and finally well look at a prediction at the first timestep
time_pred = pred[0]
print(len(time_pred))
print(time_pred)
# and of course its 65 values representing the probabillity of each character occuring next

# If we want to determine the predicted character we need to sample the output distribution (pick a value based on probabillity)
sampled_indices = tf.random.categorical(pred, num_samples=1)

# now we can reshape that array and convert all the integers to numbers to see the actual characters
sampled_indices = np.reshape(sampled_indices, (1, -1))[0]
predicted_chars = int_to_text(sampled_indices)

predicted_chars  # and this is what the model predicted for training sequence 1

"""So now we need to create a loss function that can compare that output to the expected output and give us some numeric value representing how close the two were. """

def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

"""###Compiling the Model
At this point we can think of our problem as a classification problem where the model predicts the probabillity of each unique letter coming next. 

"""

model.compile(optimizer='adam', loss=loss)

"""###Creating Checkpoints

Now we are going to setup and configure our model to save checkpoinst as it trains. This will allow us to load our model from a checkpoint and continue training it.
"""

# Directory where the checkpoints will be saved
checkpoint_dir = './training_checkpoints'
# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

"""# Training



"""

history = model.fit(data, epochs=50, callbacks=[checkpoint_callback])

"""# Prediction: Generate Text

### **Loading the Model (with epoch=1)**
We'll rebuild the model from a checkpoint using a batch_size of 1 so that we can feed one peice of text to the model and have it make a prediction.


"""

model = build_model(VOCAB_SIZE, EMBEDDING_DIM, RNN_UNITS, batch_size=1)

"""### **Save checkpoint to store weights**

Once the model is finished training, we can find the **lastest checkpoint** that stores the models weights using the following line.

"""

model.load_weights(tf.train.latest_checkpoint(checkpoint_dir)) # to get latest checkpoints
model.build(tf.TensorShape([1, None]))

"""We can load **any checkpoint** we want by specifying the exact file to load."""

# to get intermediate checkpoints

# checkpoint_num = 10
# model.load_weights(tf.train.load_checkpoint("./training_checkpoints/ckpt_" + str(checkpoint_num)))
# model.build(tf.TensorShape([1, None]))

"""### now Generating Text
Now we can use the lovely function provided by tensorflow to generate some text using any starting string we'd like.
"""

def generate_text(model, start_string):
  # Evaluation step (generating text using the learned model)

  # Number of characters to generate
  num_generate = 800

  # Converting our start string to numbers (vectorizing)
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store our results
  text_generated = []

  # Low temperatures results in more predictable text.
  # Higher temperatures results in more surprising text.
  # Experiment to find the best setting.
  temperature = 1.0

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
      predictions = model(input_eval)
      # remove the batch dimension
    
      predictions = tf.squeeze(predictions, 0)

      # using a categorical distribution to predict the character returned by the model
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      # We pass the predicted character as the next input to the model
      # along with the previous hidden state
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])

  return (start_string + ''.join(text_generated))

inp = input("Type a starting string: ")
print(generate_text(model, inp))