import json
import logging
import pandas as pd
import joblib
import os
from kafka import KafkaConsumer

# Logging setup
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FraudProcessor")

def load_model():
    """Function to load the machine learning model and scaler"""
    try:
        model_path = os.path.join('models', 'supervised_models', 'XGBoost.pkl')
        scaler_path = os.path.join('models', 'scaler_models', 'scaler.pkl')
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        logger.info("Machine Learning model and scaler loaded successfully.")
        return model, scaler
    except Exception as e:
        logger.error(f"Error loading model or scaler: {e}")
        return None, None

def process_pipeline():
    model, scaler = load_model()
    if not model or not scaler:
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
            model_features = {
                'Transaction_Amount': transaction['Transaction_Amount'],
                'hour': transaction['hour'],
                'loc_idx': transaction['loc_idx'],
                'dev_idx': transaction['dev_idx'],
                'Daily_Transaction_Count': transaction['Daily_Transaction_Count']
            }
            
            df = pd.DataFrame([model_features])
            scaled_data = scaler.transform(df)
            prob = model.predict_proba(scaled_data)[0][1]
            
            if prob > 0.95:
                logger.warning(f"!!! FRAUD DETECTED !!! | ID: {transaction.get('transaction_id')} | Confidence: {prob:.2f}")
            else:
                logger.info(f"Transaction Secure: ID {transaction.get('transaction_id')} | Confidence: {prob:.2f}")
                
        except Exception as e:
            logger.error(f"Error during processing: {e}")

if __name__ == "__main__":
    process_pipeline()
