import subprocess
import torch
import torchvision
from PIL import Image
from torchvision import transforms
import base64
import requests
import json
import argparse

# 查看原始pytorch模型的输出
transform = transforms.Compose([
    transforms.Resize((224, 224)), 
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

model = torchvision.models.densenet121(num_classes=7)
model.load_state_dict(torch.load('xxx.pth', map_location='cpu'))
model.eval()
image = Image.open('test.jpg')
img_input = transform(image).unsqueeze(0)
input_np = img_input.numpy()
pytorch_output = model(img_input).detach().numpy()
print(pytorch_output)


import tensorflow as tf
import numpy as np
from tensorflow_serving.apis import classification_pb2, input_pb2
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2, prediction_service_pb2_grpc
import grpc
from grpc.beta import implementations

# 查看tensorflow serving的结果
channel = grpc.insecure_channel('127.0.0.1:8500')
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
request = predict_pb2.PredictRequest()
request.model_spec.name = 'densenet'
request.model_spec.signature_name = 'predict_images'
request.inputs['input_img'].CopyFrom(
    tf.make_tensor_proto(img_input, shape=[1, 3, 224, 224]))
result = stub.Predict(request, 5)
channel.close()

print(result)