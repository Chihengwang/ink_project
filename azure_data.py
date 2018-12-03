'''
Basic information you would need from azure
假如說iteration_id有變的話 要記得改
'''
from azure.cognitiveservices.vision.customvision.training import training_api
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import prediction_endpoint
from azure.cognitiveservices.vision.customvision.prediction.prediction_endpoint import models
training_key = "91aa1321e04949ac84fe6f9d5485b89a"
prediction_key = "b10010f7d29f4edb8b41e32d200eb795"
project_id="32fbec84-5766-4352-83c2-8318a76e111d"
iteration_id="62ea3a31-cd5a-41a0-b9d9-403b9062f41e"