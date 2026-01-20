# Model Server and Metrics Demo

Welcome to the Model Server and Metrics demo! This repository showcases key capabilities of the Red Hat OpenShift AI platform—specifically around deploying and monitoring machine learning (ML) models at scale using KServe.

## 📌 Overview

This demo highlights the work of the Red Hat OpenShift AI Model Server and Metrics team. Our goal is to:

- Deploy and monitor containerized ML models across hybrid cloud environments.
- Enable real-time observability and ensure performance and reliability of models.
- Provide end-to-end ML lifecycle management via scalable and modular serving infrastructure.

A recording of the features showcased in this demo can be found on [YouTube](https://www.youtube.com/watch?v=OjOgmMx3B7I).

## 🎯 Demo Goals

- Show real-world use cases of serving and monitoring models on OpenShift AI.
- Demonstrate specialized features like transformers, autoscaling, and multi-node LLM support.
- Highlight tools that improve observability, performance, and reliability.

---

## 🐶 Initial Demo: Dog Breed Classification

### 🔍 Description
We deploy a lightweight image classification model that detects dog breeds from images using OpenShift AI and KServe.

### 📌 Capabilities Demonstrated

- **Basic inference service**
- **Transformer Integration:** Clean and normalize input data before inference.
- **Autoscaling (Scale to 0):** Efficient resource use with demand-based scaling.
- **Stop/Resume Annotations:** Pause/resume models for experimental workflows.
- **Metrics & Dashboards:** Real-time insight into model health and performance.

### 🔗 Demo Steps
- See: [Basic demo steps](https://github.com/hdefazio/modelservermetrics_demo/tree/main/basic_demo)
---

## 🧠 Multi-Node LLM Demo

### 📌 Problem
Large language models (LLMs) often exceed the memory limits of a single node.

### 💡 Solution
Multi-node support allows you to split a single model inference across several nodes in the cluster.


### 🔗 Demo Steps
See: [Multi-node demo steps](https://github.com/hdefazio/modelservermetrics_demo/tree/main/multi_node)

### ✅ Highlights

- Horizontally scales LLM deployments across the cluster.
- No longer constrained by single-node GPU memory.

---

## 🔗 Inference Graph Demo

### 📌 Concept
Chain multiple models together so the output of one becomes the input of the next—all behind a single endpoint.

Example:  
Dog breed → LLM poem generation about that dog → Combined response


### 🔗 Demo Steps
See: [Inference Graph demo steps](https://github.com/hdefazio/modelservermetrics_demo/tree/main/inference_graph)

### ✅ Highlights

- Simplifies application logic with a declarative graph managed by KServe.
- Provides a unified API endpoint for complex model workflows.
- Efficient resource use—each `InferenceService` can scale independently.

---
---

## 🙌 Contributors

- Hannah DeFazio – Red Hat OpenShift AI
- Mariah Holder – Red Hat OpenShift AI
