import random
import time
import json
import logging
from kafka import KafkaProducer

# Logging setup: To keep track of each step
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DataProducer")

def get_kafka_producer():
    """Function to initialize Kafka Producer"""
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
    producer = get_kafka_producer()
    if not producer:
        return

    logger.info("Starting data streaming (90% Safe, 10% Fraud)...")
    
    while True:
        try:
            # 10% chance for fraud data generation (Real-world distribution)
            is_fraudulent = random.random() < 0.10 
            
            # Creating transaction data
            transaction_data = {
                "transaction_id": random.randint(10000, 99999),
                "Transaction_Amount": float(random.uniform(45000, 80000)) if is_fraudulent else float(random.uniform(100, 5000)),
                "hour": random.randint(0, 23),
                "loc_idx": random.randint(1, 20),
                "dev_idx": random.randint(1, 10),
                "Daily_Transaction_Count": random.randint(10, 20) if is_fraudulent else random.randint(1, 5)
            }
            
            # Sending data to Kafka topic
            producer.send('transaction_stream', transaction_data)
            
            status = "FRAUD-LIKE" if is_fraudulent else "NORMAL"
            logger.info(f"Data sent -> [ID: {transaction_data['transaction_id']}] [Status: {status}] [Amount: {transaction_data['Transaction_Amount']:.2f}]")
            
            time.sleep(2) # 2-second gap
            
        except KeyboardInterrupt:
            logger.info("Stopping producer...")
            break
        except Exception as e:
            logger.error(f"Error while sending data: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
