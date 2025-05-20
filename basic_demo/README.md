# Image Transformer KServe Setup & Query Guide

This guide provides steps to set up and query an Inference Service (ISVC) with a custom image transformer.

## 🚀 Setup

Follow these steps to prepare your custom transformer image and deploy the Inference Service.

### 1. Build Transformer Image

To build and push your custom image transformer, follow these sub-steps:

a.  **Clone KServe Repository**
Begin by cloning the KServe repository to your local machine:

`bash git clone git@github.com:kserve/kserve.git `

b.  **Update Custom `model.py` File**
Copy your custom transformer logic into the KServe directory. Ensure `${KSERVE_DIR}` is set to the path where you cloned the KServe repository.

`bash cp transformer.py ${KSERVE_DIR}/kserve/python/custom_transformer/model.py `

c.  **Build and Push Image**
Navigate to the Python directory within the KServe clone and build your Docker image. Then, push it to your desired registry.

```bash 
cd ${KSERVE_DIR}/python 
podman build -t quay.io/hdefazio/image-transformer:latest -f custom_transformer.Dockerfile . 
podman push quay.io/hdefazio/image-transformer:latest
```

### 2. Create Inference Service

Once your transformer image is pushed, deploy your Inference Service using the provided YAML file.

`oc apply -f isvc.yaml`

## 🔍 Query Model

After the Inference Service is deployed and ready, you can send inference requests to your model.

### 1. Create Request from Image

First, prepare your request payload by converting an image into the required format using your Python script.

`python convert_image_to_request.py`

This script should generate a JSON file (e.g., `dog_input_request.json`) containing the image data.

### 2. Send Request

Finally, send the prepared JSON request to your KServe model endpoint using `curl`.

`curl -X POST -vk -H "Content-Type: application/json" --data-binary @./dog_input_request.json https://dog-breeds-classifier-modelserving-demo.apps.rosa.n1t3u2f3w1s0b1d.kkw2.p3.openshiftapps.com/v2/models/dog-breeds-classifier/infer `
