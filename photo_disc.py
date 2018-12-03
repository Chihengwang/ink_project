import numpy as np
import cv2
from matplotlib import pyplot as plt

test_image="./test/0.jpeg"
img = cv2.imread(test_image)
# plt.imshow(img)
# plt.show()
print(img)
print(img.shape)