# bento_services/ner_service.py


import bentoml
import logfire
import torch
from fastapi import FastAPI
from gliner import GLiNER

from bento_services.ner_config import ner_settings
from bento_services.ner_schema import NEROutput, NerRequest

# Load .env

token = ner_settings.logfire_token

# Logfire Configuration
logfire.configure(
    token=token.get_secret_value(),
    service_name="NERService",
    distributed_tracing=True,
)


image = (
    bentoml.images.Image(base_image="python:3.11.15-slim")
    .python_packages(
        "--index-url https://pypi.org/simple",
        "--extra-index-url https://download.pytorch.org/whl/cu130",

        "torch==2.13.0",

        "--extra-index-url",
        "https://pypi.org/simple",

        "gliner==0.2.24",
        "logfire==4.32.1",
        "python-dotenv==1.2.2",
        "pydantic-settings==2.14.0",
        "fastapi==0.136.1",
    )
    .run(
        'python -c "from gliner import GLiNER; '
        "GLiNER.from_pretrained('Ihor/gliner-biomed-large-v1.0')\""
    )
)
health_app = FastAPI()

@health_app.get("/ping")
async def health():
    return {"status": "ok"}

# Starting the BentoML Service
@bentoml.service(
    image=image,
    resources={"gpu": 1},
    traffic={"timeout": 300},
)
@bentoml.asgi_app(health_app)
class NERService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = GLiNER.from_pretrained(
            "Ihor/gliner-biomed-large-v1.0",
            token=ner_settings.hf_token.get_secret_value(),
        )

        self.model.to(self.device)

        # Put the model in inference/evaluation mode
        self.model.eval()

        logfire.info(
            "GliNER Initialization",
            torch=torch.__version__,
            CUDA_build=torch.version.cuda,
            CUDA_available=torch.cuda.is_available(),
            GLiNER_loaded_on=self.device,
        )

        self.labels = [
            "disease",
            "medication",
            "symptom",
            "lab test",
            "lab test value",
            "dosage",
            "drug frequency",
            "demographic information",
        ]

    # GLiNER predict
    @bentoml.api
    def extract_entities(self, request: NerRequest) -> NEROutput:


        logfire.info(
            "GliNER Input Received",
            text_length=len(request.text),
        )


        with logfire.span(
            "Gliner predict",
            text_length=len(request.text),
        ):
            # Disable gradient tracking during inference
            with torch.inference_mode():
                entities = self.model.predict_entities(
                    request.text,
                    self.labels,
                    threshold=0.5,
                )

                logfire.info(
                    "GliNER Output Completed",
                    entities_legth=len(entities),
                    entities=entities,
                )

            return NEROutput(entities=entities)
