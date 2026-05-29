import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# roberta model 
MODEL_NAME = os.getenv("MODEL_NAME", "cardiffnlp/twitter-roberta-base-sentiment")

# Fine-tuned ABSA model path 
ABSA_MODEL_PATH = os.getenv( "ABSA_MODEL_PATH", "../../Models piplines /Sentimental Analysis/models/deberta-absa")

# Controls variable to change models
SENTIMENT_BACKEND = os.getenv("SENTIMENT_BACKEND", "deberta_absa")