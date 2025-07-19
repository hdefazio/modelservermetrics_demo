import io
import argparse
#import requests
import httpx
import numpy as np
from typing import Dict, Any
from kserve import Model, ModelServer, model_server, logging, InferRequest, RESTConfig, InferenceRESTClient
from kserve.model import PredictorConfig

class TopicPromptBuilder(Model):
    """
    A standalone KServe transformer for an InferenceGraph.

    This transformer receives the V2 protocol output from a previous classifier node.
    It uses this output, along with parameters from the original request, to
    construct a new payload for a downstream vLLM service.
    """
    def __init__(self, name: str, predictor_config: PredictorConfig):
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
        self.predictor_host = predictor_config.predictor_host
        self.ready = True
        #cfg = RESTConfig(verify=False)
        #self.client = InferenceRESTClient(cfg)
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=1200.0))
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
        if type(inputs) is InferRequest:
            inputs = inputs.to_dict()
        # Extract data passed from the previous node and the original request
        try:
            previous_node_name = inputs["model_name"]
            classifier_output =inputs["outputs"][0]
            scores = classifier_output["data"]
            class_labels = ['001.Affenpinscher', '002.Afghan_hound', '003.Airedale_terrier', '004.Akita', '005.Alaskan_malamute', '006.American_eskimo_dog', '007.American_foxhound', '008.American_staffordshire_terrier', '009.American_water_spaniel', '010.Anatolian_shepherd_dog', '011.Australian_cattle_dog', '012.Australian_shepherd', '013.Australian_terrier', '014.Basenji', '015.Basset_hound', '016.Beagle', '017.Bearded_collie', '018.Beauceron', '019.Bedlington_terrier', '020.Belgian_malinois', '021.Belgian_sheepdog', '022.Belgian_tervuren', '023.Bernese_mountain_dog', '024.Bichon_frise', '025.Black_and_tan_coonhound', '026.Black_russian_terrier', '027.Bloodhound', '028.Bluetick_coonhound', '029.Border_collie', '030.Border_terrier', '031.Borzoi', '032.Boston_terrier', '033.Bouvier_des_flandres', '034.Boxer', '035.Boykin_spaniel', '036.Briard', '037.Brittany', '038.Brussels_griffon', '039.Bull_terrier', '040.Bulldog', '041.Bullmastiff', '042.Cairn_terrier', '043.Canaan_dog', '044.Cane_corso', '045.Cardigan_welsh_corgi', '046.Cavalier_king_charles_spaniel', '047.Chesapeake_bay_retriever', '048.Chihuahua', '049.Chinese_crested', '050.Chinese_shar-pei', '051.Chow_chow', '052.Clumber_spaniel', '053.Cocker_spaniel', '054.Collie', '055.Curly-coated_retriever', '056.Dachshund', '057.Dalmatian', '058.Dandie_dinmont_terrier', '059.Doberman_pinscher', '060.Dogue_de_bordeaux', '061.English_cocker_spaniel', '062.English_setter', '063.English_springer_spaniel', '064.English_toy_spaniel', '065.Entlebucher_mountain_dog', '066.Field_spaniel', '067.Finnish_spitz', '068.Flat-coated_retriever', '069.French_bulldog', '070.German_pinscher', '071.German_shepherd_dog', '072.German_shorthaired_pointer', '073.German_wirehaired_pointer', '074.Giant_schnauzer', '075.Glen_of_imaal_terrier', '076.Golden_retriever', '077.Gordon_setter', '078.Great_dane', '079.Great_pyrenees', '080.Greater_swiss_mountain_dog', '081.Greyhound', '082.Havanese', '083.Ibizan_hound', '084.Icelandic_sheepdog', '085.Irish_red_and_white_setter', '086.Irish_setter', '087.Irish_terrier', '088.Irish_water_spaniel', '089.Irish_wolfhound', '090.Italian_greyhound', '091.Japanese_chin', '092.Keeshond', '093.Kerry_blue_terrier', '094.Komondor', '095.Kuvasz', '096.Labrador_retriever', '097.Lakeland_terrier', '098.Leonberger', '099.Lhasa_apso', '100.Lowchen', '101.Maltese', '102.Manchester_terrier', '103.Mastiff', '104.Miniature_schnauzer', '105.Neapolitan_mastiff', '106.Newfoundland', '107.Norfolk_terrier', '108.Norwegian_buhund', '109.Norwegian_elkhound', '110.Norwegian_lundehund', '111.Norwich_terrier', '112.Nova_scotia_duck_tolling_retriever', '113.Old_english_sheepdog', '114.Otterhound', '115.Papillon', '116.Parson_russell_terrier', '117.Pekingese', '118.Pembroke_welsh_corgi', '119.Petit_basset_griffon_vendeen', '120.Pharaoh_hound', '121.Plott', '122.Pointer', '123.Pomeranian', '124.Poodle', '125.Portuguese_water_dog', '126.Saint_bernard', '127.Silky_terrier', '128.Smooth_fox_terrier', '129.Tibetan_mastiff', '130.Welsh_springer_spaniel', '131.Wirehaired_pointing_griffon', '132.Xoloitzcuintli', '133.Yorkshire_terrier']
            initial_prompt = "Write a fun poem"
            target_model_name = "vllm-llama3-8b"
        except Exception as e:
            raise ValueError(f"Issue grabbing data from input.Error: {e}\n input: {inputs}\n")

        # Determine the detected class.
        predicted_index = np.argmax(scores)
        detected_class = class_labels[predicted_index]

        # Construct the new prompt string for the LLM.
        new_prompt = f"{initial_prompt} about the following topic: {detected_class}"

        # Format the new payload to match the vLLM completions API.
        new_payload = {
            "model": target_model_name,
            "prompt": new_prompt,
            "max_tokens": 100,
            "temperature": 0
        }

        return new_payload
    
    async def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        """
        Overrides the default predict handler to call the vLLM's custom endpoint.

        Args:
            payload (Dict): The dictionary returned by the preprocess function.
            headers (Dict): Request headers.

        Returns:
            Dict: The JSON response from the vLLM predictor.
        """
        outbound_headers = {
            "Content-Type": "application/json"
        }

        # Construct the full URL to the predictor's completions endpoint
        predictor_url = "http://vllm-llama3-8b-predictor-modelserving-demo.apps.rosa.n1t3u2f3w1s0b1d.kkw2.p3.openshiftapps.com/v1/completions"
        print(f"Sending request to predictor at: {predictor_url}")

        # Send the request to the vLLM predictor
        response = await self.client.post(predictor_url, json=payload, headers=outbound_headers)
        
        # Raise an exception if the request failed
        response.raise_for_status()

        return response.json()


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
