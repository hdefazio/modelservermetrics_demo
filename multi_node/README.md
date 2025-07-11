# Multi-Node KServe Setup & Query Guide

This guide provides steps to set up and query an Inference Service (ISVC) using multi-node.

## 📋 Prerequisites

You are logged into an OpenShift cluster using the oc CLI.

You have a Hugging Face access token with permissions to download the Llama 3 model.

## 🚀 Setup: Prepare Model and Storage
First, we'll create a Persistent Volume Claim (PVC) and download the model files to it.

### 1. Clone the Repository

```bash 
git clone https://github.com/Jooho/jhouse_openshift.git
cd jhouse_openshift/Kserve/poc/multi-node/kserve-vllm-multinode
```

### 2. Create the PVC

`oc apply -f 1.create-pvc.yaml`

### 3. Download the Model
```bash 
# Replace XXX with your actual Hugging Face token
export HF_TEST_TOKEN=XXX
export MODEL=meta-llama/Meta-Llama-3-8B-Instruct
# Update memory size to 15Gi for limit in download-model container
```

```bash
# The envsubst command replaces the variables in the YAML file before applying it
cat 2.download-model-to-pvc.yaml|envsubst |oc apply -f -
```
Note: The download pod requests 15Gi of memory. You can monitor its progress by checking the pod logs in the modelserving-demo namespace.


## 🚀 Setup: Deploy the Inference Service
### 1. Create the vLLM Serving Runtime

```bash
oc apply -f .vllm-servingruntime-multinode.yaml
oc apply -f 6.vllm-isvc-pvc.yaml
```

### 2. Apply the Inference Service
This deploys your model, referencing the runtime and the model files in the PVC.

`oc apply -f isvc.yaml`

### 3. (Optional) Add to OpenDataHub Dashboard

To make the model visible on the OpenDataHub dashboard, ensure the InferenceService metadata includes the following label:
```
labels:
    opendatahub.io/dashboard: 'true'
```

## 🔍 Inference Request
After the Inference Service is deployed and ready, you can send inference requests to your model.

### Option 1: Python notebook
Run the provided `vllm_demo.ipynb` in a pytorch workbench on the cluster

### Option 2: Command line
#### Get the Public URL
```bash
oc expose service vllm-llama3-8b-predictor
export PUBLIC_URL=$(oc get route vllm-llama3-8b-predictor -n modelserving-demo -o jsonpath='{"http://"}{.spec.host}{"\n"}')
```

#### Send an Inference Request
``` 
oc exec vllm-llama3-8b-predictor-6864b5c6d-gnwzd -n modelserving-demo -- curl ${PUBLIC_URL}/v1/completions  -H "Content-Type: application/json" \
    -d '{
        "model": "vllm-llama3-8b",
        "prompt": "Write a poem about a dog",
        "max_tokens": 100,
        "temperature": 0
    }'
```
