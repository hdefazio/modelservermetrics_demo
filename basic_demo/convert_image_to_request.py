# source: https://github.com/Jooho/minio-model-storage/blob/main/docs/openvino/age-gender-recognition/convert_image.py
import numpy as np
from PIL import Image

# You can check input/output from runtime pod 
#[2024-06-03 22:51:11.922][1][modelmanager][info][modelinstance.cpp:453] Input name: data; mapping_name: data; shape: (1,3,62,62); precision: FP32; layout: NCHW
#[2024-06-03 22:51:11.922][1][modelmanager][info][modelinstance.cpp:501] Output name: prob; mapping_name: prob; shape: (1,2,1,1); precision: FP32; layout: N...
#[2024-06-03 22:51:11.922][1][modelmanager][info][modelinstance.cpp:501] Output name: age_conv3; mapping_name: age_conv3; shape: (1,1,1,1); precision: FP32; layout: N...

# Load your image
img = Image.open('Dog_Breeds.jpg')

# Convert the image to a numpy array and ensure it is in RGB format
img_array = np.array(img.convert('RGB'))

# by default, th array order show (height, width, channel) but this model want (channel, height, width) so change the array order
# Transpose the image array from NHWC to NCHW format(channel, height, width)
img_array = np.transpose(img_array, (2, 0, 1))

# Check the shape of the image
print(img_array.shape)  # Should be (height, width, channels)

# Ensure the array is in NHWC format (this should be the case already if using PIL Image)
#if img_array.ndim == 3:
#    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

print(img_array.shape)  # Should be (1, height, width, channels)

import json

# Assuming you have the rest of the request data in a dictionary `request_data`
request_data = {
    "inputs": [{
        "name": "data",
        "shape": img_array.shape,
        "datatype": "FP32",  # Adjust as necessary
        "data": img_array.tolist()
    }]
}

# Save to a JSON file
with open('3dog_input_request.json', 'w') as f:
    json.dump(request_data, f)
