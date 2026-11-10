import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import cv2
from PIL import Image
import pickle

np.random.seed(44)

def main():
  # Load and preprocess CIFAR-10 data
  X_train, y_train, X_test, y_test, class_names = load_combined_data()
  num_classes = len(class_names)

  # Create validation data
  X_train, X_val, y_train, y_val = create_val_data(X_train, y_train)
  # Check original data
  print("Original data:")
  check_data(X_train, y_train, X_val, y_val, X_test, y_test, class_names)

  # Show training samples and their distribution
  num_of_each_sign = show_training_samples(X_train, y_train, class_names, num_classes)
  plot_sample_distribution(num_classes, num_of_each_sign)
  examine_typical_image(X_train, y_train)

  # Image preprocessing
  X_train, X_val, X_test = apply_preprocessing(X_train, X_val, X_test)
  examine_random_training_image_after_preprocessing(X_train)
  # Show sample images after preprocessing
  num_of_each_sign = show_training_samples(X_train, y_train, class_names, num_classes)

  datagen = create_data_generator()
  explore_datagen(datagen, X_train, y_train)


def explore_datagen(datagen, X_train, y_train):
  datagen.fit(X_train)
  batches = datagen.flow(X_train, y_train, batch_size=20)
  X_batch, y_batch = next(batches)
  fig, axs = plt.subplots(1, 15, figsize=(20,5))
  fig.tight_layout()
  for i in range(15):
    axs[i].imshow(X_batch[i].reshape(32, 32))
    axs[i].axis("off")
  plt.show()


def create_data_generator():
  datagen = ImageDataGenerator(
      rotation_range=10,
      width_shift_range=0.1,
      height_shift_range=0.1,
      zoom_range=0.2,
      shear_range=0.1
  )
  return datagen


def examine_random_training_image_after_preprocessing(X_train):
  plt.imshow(X_train[np.random.randint(0, len(X_train)-1)])
  plt.axis('off')
  plt.show()
  print(X_train.shape)


def apply_preprocessing(X_train, X_val, X_test):
  X_train = np.array(list(map(preprocessing, X_train)))
  X_val = np.array(list(map(preprocessing, X_val)))
  X_test = np.array(list(map(preprocessing, X_test)))
  return X_train, X_val, X_test


def preprocessing(img):
  img = grayscale(img)
  img = equalize(img)
  img = img/255
  return img


def grayscale(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return img


def equalize(img):
  img = cv2.equalizeHist(img)
  return img


def examine_typical_image(X_train, y_train):
  pre_img = X_train[1222]
  plt.imshow(pre_img)
  plt.title(f"Label: {y_train[1222]}")
  plt.show()


def plot_sample_distribution(num_classes, num_of_each_sign):
  plt.figure(figsize=(12,4))
  plt.bar(range(0, num_classes), num_of_each_sign)
  plt.title("Distribution of the training set")
  plt.xlabel("Class number")
  plt.ylabel("Number of images")
  plt.show() 


def show_training_samples(X_train, y_train, class_names, num_classes):
  num_samples = []
  cols = 5
  rng = np.random.default_rng(44)

  fig, axes = plt.subplots(num_classes, ncols = cols, figsize=(cols*2, num_classes*2))
  for i in range(num_classes):
    x_selected = X_train[y_train == i] # select images belonging to the current class
    # select 5 random samples from the current class
    selected_samples = rng.choice(x_selected.shape[0], size=cols, replace=False) 
    for j, idx in enumerate(selected_samples):
      axes[i, j].imshow(x_selected[idx])
      axes[i, j].axis('off')
      if j == 0: # dispaly class name for the first column of each row
        axes[i, j].set_title(class_names[i])
    num_samples.append(len(x_selected))

  plt.tight_layout()
  plt.show()
  return num_samples


def filter_selected_classes(X, y, selected_classes): # https://numpy.org/doc/2.2/reference/generated/numpy.isin.html
  mask = np.isin(y, selected_classes) # keep only the samples whose labels are in the selected classes, using a boolean mask
  return X[mask], y[mask]


def select_classes(X_train, y_train, X_val, y_val, X_test, y_test, class_names):
  selected_classes= [1,2,3,4,5,7,9]

  X_train, y_train = filter_selected_classes(X_train, y_train, selected_classes)
  X_val, y_val = filter_selected_classes(X_val, y_val, selected_classes)
  X_test, y_test = filter_selected_classes(X_test, y_test, selected_classes)

  # Update class names to only include selected classes
  label_mapping = {
    original: new
    for new, original in enumerate(selected_classes)
  }

  # Replace original labels with new labels according to the mapping
  y_train = np.array([label_mapping[label] for label in y_train])
  y_val = np.array([label_mapping[label] for label in y_val])
  y_test = np.array([label_mapping[label] for label in y_test])

  selected_class_names = [class_names[i] for i in selected_classes]

  return X_train, y_train, X_val, y_val, X_test, y_test, selected_class_names



def check_data(X_train, y_train, X_val, y_val, X_test, y_test, class_names):
  print("Training data shape:", X_train.shape)
  print("Training labels shape:", y_train.shape)
  print("Validation data shape:", X_val.shape)
  print("Validation labels shape:", y_val.shape)
  print("Test data shape:", X_test.shape)
  print("Test labels shape:", y_test.shape)
  print("Class names:", class_names)

  assert(X_train.shape[0] == y_train.shape[0]), "The number of training samples does not match the number of labels"
  assert(X_val.shape[0] == y_val.shape[0]), "The number of validation samples does not match the number of labels"
  assert(X_test.shape[0] == y_test.shape[0]), "The number of test samples does not match the number of labels"
  assert(X_train.shape[1:] == (32, 32, 3)), "The dimensions of the training images are not (32, 32, 3)"
  assert(X_val.shape[1:] == (32, 32, 3)), "The dimensions of the validation images are not (32, 32, 3)"
  assert(X_test.shape[1:] == (32, 32, 3)), "The dimensions of the test images are not (32, 32, 3)"


def create_val_data(X_train, y_train):
  return train_test_split(
    X_train, 
    y_train, 
    test_size=0.2, 
    random_state=44,
    stratify=y_train
    )


def unpickle(file):
  with open(file, 'rb') as f:
    return pickle.load(f, encoding='bytes')


def select_and_remap(X, y, groups, offset=0):
  # groups: list of (new_name, [original indices]); several originals can share one new label
  label_mapping = {}
  for new, (_, originals) in enumerate(groups, start=offset):
    for original in originals:
      label_mapping[original] = new

  mask = np.isin(y, list(label_mapping.keys()))
  X, y = X[mask], y[mask]
  y = np.array([label_mapping[label] for label in y])

  new_names = [name for name, _ in groups]
  return X, y, new_names


def load_combined_data(): # https://claude.ai/share/1577e5f3-7a02-4538-a5ce-40ed4b0b422b
  X10_train, y10_train, X10_test, y10_test, names10 = load_cifar10_data()
  X100_train, y100_train, X100_test, y100_test, names100 = load_cifar100_data()

  selected10 = [1, 2, 3, 4, 5, 7, 9]
  groups10 = [(names10[i], [i]) for i in selected10]

  def idx(*names):
    return [names100.index(n) for n in names]   # <- names100, not names10

  groups100 = [(n, idx(n)) for n in [
    "cattle", "fox", "baby", "boy", "girl", "man", "woman", "rabbit",
    "squirrel", "bicycle", "bus", "motorcycle", "pickup_truck", "train",
    "lawn_mower", "tractor"
  ]]
  groups100.append(("tree", idx("maple_tree", "oak_tree", "palm_tree",
                                "pine_tree", "willow_tree")))

  X10_train, y10_train, n10 = select_and_remap(X10_train, y10_train, groups10, offset=0)
  X10_test,  y10_test,  _   = select_and_remap(X10_test,  y10_test,  groups10, offset=0)

  offset = len(groups10)
  X100_train, y100_train, n100 = select_and_remap(X100_train, y100_train, groups100, offset=offset)
  X100_test,  y100_test,  _    = select_and_remap(X100_test,  y100_test,  groups100, offset=offset)

  X_train = np.concatenate([X10_train, X100_train], axis=0)
  y_train = np.concatenate([y10_train, y100_train], axis=0)
  X_test  = np.concatenate([X10_test,  X100_test],  axis=0)
  y_test  = np.concatenate([y10_test,  y100_test],  axis=0)

  return X_train, y_train, X_test, y_test, n10 + n100


def load_cifar100_data():
  data_dir = "cifar-100-python"

  train_data = unpickle(os.path.join(data_dir, "train"))
  X_train = train_data[b'data']
  y_train = np.array(train_data[b'fine_labels'])

  test_data = unpickle(os.path.join(data_dir, "test"))
  X_test = test_data[b'data']
  y_test = np.array(test_data[b'fine_labels'])

  X_train = X_train.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
  X_test = X_test.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)

  meta = unpickle(os.path.join(data_dir, "meta"))
  class_names = [name.decode('utf-8') for name in meta[b'fine_label_names']]

  return X_train, y_train, X_test, y_test, class_names


def load_cifar10_data():
  data_dir = "cifar-10-batches-py"

  # load training data from the 5 batches
  train_batches = [
    unpickle(os.path.join(data_dir, f"data_batch_{i}"))
    for i in range(1, 6)
  ]

  X_train = np.concatenate(
    [batch[b'data'] for batch in train_batches],
    axis=0
  )

  y_train = np.concatenate([
    np.array(batch[b"labels"])
    for batch in train_batches
  ])

  # load test data
  test_data = unpickle(os.path.join(data_dir, "test_batch"))
  X_test = test_data[b'data']
  y_test = np.array(test_data[b'labels'])

  # reshape the data to (num_samples, 32, 32, 3)
  X_train = X_train.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
  X_test = X_test.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)

  # load class names
  meta = unpickle(os.path.join(data_dir, "batches.meta"))
  class_names = [name.decode('utf-8') for name in meta[b'label_names']]

  return X_train, y_train, X_test, y_test, class_names


if __name__ == "__main__":
  main()