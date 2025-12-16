"""
Configuration module for queue-sample
Reads settings from environment variables
"""

import os

# Queue type: 'memory' or 'kafka'
QUEUE_TYPE = os.environ.get("QUEUE_TYPE", "memory").lower()

# In-memory queue configuration
# Number of worker threads for in-memory queue (simulates Kafka partitions)
# Each worker owns one partition, messages are routed by user_id hash
# Only applies when QUEUE_TYPE='memory', ignored for Kafka
MEMORY_QUEUE_NUM_WORKERS = int(os.environ.get("MEMORY_QUEUE_NUM_WORKERS", "1"))

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "queue-sample-topic")
KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "queue-sample-consumer-group")
