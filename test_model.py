import requests
import numpy as np
import cv2
from PIL import Image
from main import preprocessing
from tensorflow.keras.models import load_model
import json


model = load_model("cifar_model.keras")
with open("class_names.json", "r") as f:
  class_names = json.load(f)


def main():
  url_automobile = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/automobile5.png"
  url_bird = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/bird4.png"
  url_cat = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/cat9.png"
  url_deer = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/deer7.png"
  url_dog = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/dog4.png"
  url_horse = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/horse5.png"
  url_truck = "https://cave.cs.toronto.edu/kriz/cifar-10-sample/truck4.png"
  test_model_with_image(model, url_automobile)
  test_model_with_image(model, url_bird)
  test_model_with_image(model, url_cat)
  test_model_with_image(model, url_deer)
  test_model_with_image(model, url_dog)
  test_model_with_image(model, url_horse)
  test_model_with_image(model, url_truck)


def test_model_with_image(model, image_to_test):
  r = requests.get(image_to_test, stream=True)
  img = Image.open(r.raw).convert("RGB")
  img = np.asarray(img)
  img = cv2.resize(img, (32, 32))
  img = preprocessing(img)
  img = img.reshape(1, 32, 32, 1)
  prediction = model.predict(img)
  predicted_index = np.argmax(prediction)
  confidence = prediction[0][predicted_index] * 100
  print(f"Predicted class: {predicted_index} ({class_names[predicted_index]}) - {confidence:.1f}% confidence")


if __name__ == "__main__":
  main()