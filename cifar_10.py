import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import cv2
from PIL import Image
import pickle

np.random.seed(44)

def main():
  num_classes = 7

  # Load and preprocess CIFAR-10 data
  X_train, y_train, X_test, y_test, class_names = load_cifar10_data()

  # Create validation data
  X_train, X_val, y_train, y_val = create_val_data(X_train, y_train)
  # Check original data
  print("Original data:")
  check_data(X_train, y_train, X_val, y_val, X_test, y_test, class_names)

  # Select specific classes from the dataset
  X_train, y_train, X_val, y_val, X_test, y_test, class_names = select_classes(X_train, y_train, X_val, y_val, X_test, y_test, class_names)
  # Check data after selecting specific classes
  print("\nData after selecting specific classes:")
  check_data(X_train, y_train, X_val, y_val, X_test, y_test, class_names)


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