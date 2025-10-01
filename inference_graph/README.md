# Inference Graph KServe Setup & Query Guide

This guide provides steps to set up and query an Inference Graph (IG) using the previous two models as steps in the sequence.

## 📋 Prerequisites

You are logged into an OpenShift cluster using the oc CLI.

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
cp topic_prompt_builder_transformer.py ${KSERVE_DIR}/python/custom_transformer/model.py
```

c.  **Build and Push Image**
Navigate to the Python directory within the KServe clone and build your Docker image. Then, push it to your desired registry.

```bash 
cd ${KSERVE_DIR}/python 
podman login quay.io/hdefazio/topic-prompt-builder-transformer
podman build -t quay.io/hdefazio/topic-prompt-builder-transformer:latest -f custom_transformer.Dockerfile . 
podman push quay.io/hdefazio/topic-prompt-builder-transformer:latest
```
Make the repository public in quay

### 2. Update the vllm ISVC
Copy the contents of the `vllm_transformer.yaml` file to the `vllm-llama3-8b` `spec` field

### 3. Deploy the Inference Graph

```bash
oc apply -f inference_graph.yaml
```

## 🔍 Inference Request

After the Inference Service is deployed and ready, you can send inference requests to your model.

### Option 1: Python notebook

Run the provided `inference_graph_demo.ipynb` in a pytorch workbench on the cluster
