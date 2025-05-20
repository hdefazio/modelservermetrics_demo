import argparse
from typing import Dict
import numpy as np
import io
from PIL import Image
from torchvision import transforms
from kserve import Model, ModelServer, model_server, InferInput, InferRequest, logging
from kserve.model import PredictorProtocol, PredictorConfig


def image_transform(arr):
    img_transform = transforms.Compose([
        transforms.Resize(254),
        transforms.CenterCrop(254),
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
    def __init__(self, name: str, predictor_config: PredictorConfig,):
        super().__init__(
            name,
            predictor_config,
            return_response_headers=True,
        )
        self.model_name = name
        self.ready = True

    def preprocess(
        self, request: InferRequest, headers: Dict[str, str] = None
    ) -> InferRequest:
        input_tensors = [
            image_transform(instance) for instance in request.inputs[0].data
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
            model_name=self.model_name, model_version="v2", infer_inputs=infer_inputs
        )
        return infer_request


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
