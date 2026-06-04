import json
import logging
import pandas as pd
import joblib
from kafka import KafkaConsumer

# Logging setup: To keep detailed records of each step
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FraudProcessor")

def load_model():
    """Function to load the machine learning model"""
    try:
        model = joblib.load('xgb_fraud_model.pkl')
        logger.info("Machine Learning model loaded successfully.")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def process_pipeline():
    model = load_model()
    if not model:
        return

    # Initialize Kafka Consumer
    consumer = KafkaConsumer(
        'transaction_stream',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    logger.info("Pipeline is ready, waiting for transactions...")

    for message in consumer:
        transaction = message.value
        try:
            # Creating DataFrame
            df = pd.DataFrame([transaction])
            
            # Prediction and Probability
            prob = model.predict_proba(df)[0][1]
            
            # 95% probability threshold (for higher accuracy)
            if prob > 0.95:
                logger.warning(f"!!! FRAUD DETECTED !!! | ID: {transaction['transaction_id']} | Confidence: {prob:.2f}")
            else:
                logger.info(f"Transaction Secure: ID {transaction['transaction_id']} | Confidence: {prob:.2f}")
                
        except Exception as e:
            logger.error(f"Error during processing: {e}")

if __name__ == "__main__":
    process_pipeline()
