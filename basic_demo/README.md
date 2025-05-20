# Setup
1. build transformer image
    a. Clone kserve
    $ git clone git@github.com:kserve/kserve.git

    b. Update custom model.py file
    $ cp transformer.py ${KSERVE_DIR}$/kserve/python/custom_transformer/model.py 

    c. build + push image
    $ cd ${KSERVE_DIR}/python
    $ podman build -t quay.io/hdefazio/image-transformer:latest -f custom_transformer.Dockerfile .
    $ podman push  quay.io/hdefazio/image-transformer:latest

2. Create inference service
    $ oc apply -f isvc.yaml

# Query model
1. Create request from image

$ python convert_image_to_request.py

2. Send request

$ curl -X POST -vk -H "Content-Type: application/json" --data-binary @./dog_input_request.json https://dog-breeds-classifier-modelserving-demo.apps.rosa.n1t3u2f3w1s0b1d.kkw2.p3.openshiftapps.com/v2/models/dog-breeds-classifier/infer 
