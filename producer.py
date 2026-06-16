import random
import time
import json
import logging
import joblib
import pandas as pd
import os
from kafka import KafkaProducer

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DataProducer")

def load_model():
    model_path = os.path.join("models", "supervised_models", "XGBoost.pkl")
    scaler_path = os.path.join("models", "scaler_models", "scaler.pkl")
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logger.info("Models loaded successfully for production.")
        return model, scaler
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return None, None

def get_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        logger.info("Kafka Producer started successfully.")
        return producer
    except Exception as e:
        logger.error(f"Error starting Kafka Producer: {e}")
        return None

def main():
    model, scaler = load_model()
    producer = get_kafka_producer()
    
    if not model or not producer:
        return

    logger.info("Starting production streaming with model integration...")
    
    while True:
        try:
            is_fraudulent = random.random() < 0.10 
            
            transaction_data = {
                "transaction_id": random.randint(10000, 99999),
                "Transaction_Amount": float(random.uniform(45000, 80000)) if is_fraudulent else float(random.uniform(100, 5000)),
                "hour": random.randint(0, 23),
                "loc_idx": random.randint(1, 20),
                "dev_idx": random.randint(1, 10),
                "Daily_Transaction_Count": random.randint(10, 20) if is_fraudulent else random.randint(1, 5)
            }
            
            features = pd.DataFrame([{
                'Transaction_Amount': transaction_data['Transaction_Amount'],
                'hour': transaction_data['hour'],
                'loc_idx': transaction_data['loc_idx'],
                'dev_idx': transaction_data['dev_idx'],
                'Daily_Transaction_Count': transaction_data['Daily_Transaction_Count']
            }])
            
            scaled_features = scaler.transform(features)
            prediction = model.predict(scaled_features)[0]
            
            transaction_data['prediction_status'] = "FRAUD" if prediction == 1 else "LEGIT"
            producer.send('transaction_stream', transaction_data)
            
            logger.info(f"Sent -> ID: {transaction_data['transaction_id']} | Status: {transaction_data['prediction_status']} | Amount: {transaction_data['Transaction_Amount']:.2f}")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            logger.info("Stopping producer...")
            break
        except Exception as e:
            logger.error(f"Error while sending data: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
