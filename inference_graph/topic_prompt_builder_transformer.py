import io
import argparse
import numpy as np
from typing import Dict, Any
from kserve import Model, ModelServer, model_server, logging, InferRequest
from kserve.model import PredictorConfig

class TopicPromptBuilder(Model):
    """
    A standalone KServe transformer for an InferenceGraph.

    This transformer receives the V2 protocol output from a previous classifier node.
    It uses this output, along with parameters from the original request, to
    construct a new payload for a downstream vLLM service.
    """
    def __init__(self, name: str, predictor_host: str):
        """
        Initializes the model.

        Args:
            name (str): The name of this transformer model.
            predictor_host (str): The internal host of the next node in the graph.
                                  KServe requires this, but the graph router handles
                                  the actual request forwarding.
        """
        super().__init__(name)
        self.name = name
        self.predictor_host = predictor_host
        self.ready = True
        print(f"Initialized TopicPromptBuilder transformer '{self.name}'.")

    async def preprocess(self, inputs: InferRequest, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Transforms the output from the classifier into a new prompt for the LLM.

        Args:
            inputs (InferRequest): The InferRequest from the previous step (the classifier).
                                   The InferenceGraph router automatically merges the original
                                   request's 'parameters' into this payload.
            headers (Dict): Request headers.

        Returns:
            Dict: A new JSON payload structured for the vLLM completions endpoint.
        """
        print(f"Received inputs for preprocessing: {inputs}")

        # --- Extract data passed from the previous node and the original request ---
        parameters = inputs["parameters"]
        if not parameters:
            raise ValueError(f"Parameters block is missing from the request. inputs: {inputs}")

        # 1. Get the classifier's prediction scores using object attribute access.
        previous_node_name = "dog-breeds-classifier"
        classifier_response_dict = parameters.get(previous_node_name)
        if not classifier_response_dict:
            raise ValueError(f"Output from previous step '{previous_node_name}' not found in request parameters. parameters: {parameters}")

        classifier_output = classifier_response_dict['outputs'][0]
        scores = classifier_output.data

        # 2. Get configuration from the original request's parameters.
        class_labels = parameters.get("class_labels")
        if not class_labels:
            raise ValueError("'class_labels' not found in request parameters.")

        initial_prompt = parameters.get("initial_prompt", "Write a short summary")
        target_model_name = parameters.get("target_model_name", "vllm-llama3-8b")

        # --- Perform the core logic ---

        # 3. Determine the detected class.
        predicted_index = np.argmax(scores)
        detected_class = class_labels[predicted_index]
        print(f"Detected class: '{detected_class}'")

        # 4. Construct the new prompt string for the LLM.
        new_prompt = f"{initial_prompt} about the following topic: {detected_class}"
        print(f"Constructed new prompt: '{new_prompt}'")

        # 5. Format the new payload to match the vLLM completions API.
        new_payload = {
            "model": target_model_name,
            "prompt": new_prompt,
            "max_tokens": 100,
            "temperature": 0
        }

        print(f"Returning new payload for LLM: {new_payload}")
        return new_payload

def transformer_main(args): 
    if args.configure_logging:
        logging.configure_logging(args.log_config_file)
    model = TopicPromptBuilder(
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
