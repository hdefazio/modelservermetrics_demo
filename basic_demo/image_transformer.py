import io
import argparse
import numpy as np
from PIL import Image
from typing import Dict, Union
from torchvision import transforms
from kserve import Model, ModelServer, model_server, InferInput, InferRequest, InferResponse, logging
from kserve.model import PredictorConfig


def image_transform(arr):
    img_transform = transforms.Compose([
        transforms.Resize(224),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    nparr = np.asarray(arr).astype(np.uint8)
    if nparr.shape[0] == 3:
        # (channels, height, width) -> (height, width, channels)
        nparr = np.transpose(nparr, (1, 2, 0))

    image = Image.fromarray(nparr, 'RGB')
    tensor = img_transform(image).numpy()
    
    return tensor

class ImageTransformer(Model):
    def __init__(self, name: str, predictor_config: PredictorConfig):
        super().__init__(name, predictor_config)
        self.model_name = name
        self.ready = True

    def preprocess(
        self, request: InferRequest, headers: Dict[str, str] = None
    ) -> InferRequest:
        if type(request) is InferRequest:
            request = request.to_dict()
        
        inputs = request["inputs"]
        input_tensors = [
            image_transform(instance) for instance in inputs[0]["data"]
        ]
        input_tensors = np.asarray(input_tensors)

        infer_inputs = [
            InferInput(
                name="input.1",
                datatype="FP32",
                shape=list(input_tensors.shape),
                data=input_tensors,
            )
        ]
        infer_request = InferRequest(
            model_name=self.model_name, infer_inputs=infer_inputs
        )
        return infer_request
    
    async def postprocess(
        self,
        result: Union[Dict, InferResponse],
        headers: Dict[str, str] = None,
        response_headers: Dict[str, str] = None,
    ) -> Union[Dict, InferResponse]:
        # Fixes issue where the header claims that the response is compressed when it is not
        if response_headers.get('content-encoding', '') == 'gzip':
          del response_headers['content-encoding']
        return result


def transformer_main(args): 
    if args.configure_logging:
        logging.configure_logging(args.log_config_file)
    model = ImageTransformer(
        args.model_name,
        PredictorConfig(
            args.predictor_host,
            args.predictor_protocol,
            args.predictor_use_ssl,
            args.predictor_request_timeout_seconds,
            args.predictor_request_retries,
            args.enable_predictor_health_check,
        ),
    )
    ModelServer().start([model])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(parents=[model_server.parser])
    args, _ = parser.parse_known_args()

    transformer_main(args)
