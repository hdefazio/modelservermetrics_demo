# Image Transformer KServe Setup & Query Guide

This guide provides steps to set up and query an Inference Service (ISVC) with a custom image transformer.

## 📋 Prerequisites

You are logged into an OpenShift cluster using the oc CLI.

You are logged in to a cluster with a data connection to the s3 bucket `hannahs3bucket` already configured

You have a Hugging Face access token with permissions to download the Llama 3 model.

## 🚀 Setup

Follow these steps to prepare your custom transformer image and deploy the Inference Service.

### 1. Build Transformer Image

To build and push your custom image transformer, follow these sub-steps:

a.  **Clone KServe Repository**
Begin by cloning the KServe repository to your local machine:

`git clone git@github.com:kserve/kserve.git `

b.  **Update Custom `model.py` File**
Copy your custom transformer logic into the KServe directory. Ensure `${KSERVE_DIR}` is set to the path where you cloned the KServe repository.

```bash
export KSERVE_DIR=/path/to/kserve
cp image_transformer.py ${KSERVE_DIR}/python/custom_transformer/model.py
```

c.  **Build and Push Image**
Navigate to the Python directory within the KServe clone and build your Docker image. Then, push it to your desired registry.

```bash 
cd ${KSERVE_DIR}/python 
podman login quay.io/hdefazio/image-transformer
podman build -t quay.io/hdefazio/image-transformer:latest -f custom_transformer.Dockerfile . 
podman push quay.io/hdefazio/image-transformer:latest
```

Make the repository public in quay

### 2. Create Inference Service
Create the serving runtime using the provided YAML file.

`oc apply -f servingruntime.yaml`


Deploy your Inference Service using the provided YAML file.

`oc apply -f isvc.yaml`

## 🔍 Inference Request

After the Inference Service is deployed and ready, you can send inference requests to your model.

### Option 1: Python notebook

Run the provided `dog_breeds_classifier_demo.ipynb` in a pytorch workbench on the cluster

### Option 2: Command line

#### 1. Create Request from Image

a.  **Download the image conversion script**

`curl -o convert_image_to_request.py https://raw.githubusercontent.com/Jooho/minio-model-storage/refs/heads/main/docs/openvino/age-gender-recognition/convert_image.py `

Then, change the image and json filepaths in the script. We suggest using the provided `dog.jpg` as your input and `dog_input_request.json` as your output. 

b. **Prepare your request payload by converting an image into the required format using your Python script**

`python convert_image_to_request.py`

This script should generate a JSON file (e.g., `dog_input_request.json`) containing the image data.

#### 2. Send Request

Finally, send the prepared JSON request to your KServe model endpoint using `curl`.

`curl -X POST -vk -H "Content-Type: application/json" --data-binary @./dog_input_request.json https://dog-breeds-classifier-modelserving-demo.apps.rosa.n1t3u2f3w1s0b1d.kkw2.p3.openshiftapps.com/v2/models/dog-breeds-classifier/infer`
