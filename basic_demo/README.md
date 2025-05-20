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
`bash cd ${KSERVE_DIR}/python podman build -t quay.io/hdefazio/image-transformer:latest -f custom_transformer.Dockerfile . podman push quay.io/hdefazio/image-transformer:latest `

### 2. Create Inference Service

Once your transformer image is pushed, deploy your Inference Service using the provided YAML file.
`oc apply -f isvc.yaml`
