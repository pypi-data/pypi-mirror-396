"""
Queue Monitor - Monitor and assert RabbitMQ messages during tests
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional
from queue import Queue, Empty

import pika
from pika.exceptions import AMQPConnectionError

from .config import RabbitMQConfig

logger = logging.getLogger(__name__)


class QueueMonitor:
    """
    Monitor RabbitMQ queues and capture messages during tests.
    
    Features:
    - Subscribe to queues and capture messages
    - Assert messages with specific content
    - Wait for messages with timeout
    - Message filtering and counting
    - Background consumer thread
    """
    
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.captured_messages: Dict[str, List[Dict[str, Any]]] = {}
        self.consumer_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"✅ Connected to RabbitMQ: {self.config.host}:{self.config.port}")
        except AMQPConnectionError as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    def start_monitoring(self, queue_name: str):
        """
        Start monitoring a queue in a background thread.
        
        Args:
            queue_name: Name of the queue to monitor
        """
        if queue_name in self.consumer_threads:
            logger.warning(f"⚠️ Already monitoring queue: {queue_name}")
            return
        
        self.captured_messages[queue_name] = []
        self.stop_flags[queue_name] = threading.Event()
        
        thread = threading.Thread(
            target=self._consume_messages,
            args=(queue_name,),
            daemon=True
        )
        thread.start()
        self.consumer_threads[queue_name] = thread
        
        logger.info(f"🎧 Started monitoring queue: {queue_name}")
    
    def _consume_messages(self, queue_name: str):
        """
        Background consumer for a specific queue.
        
        Args:
            queue_name: Queue to consume from
        """
        try:
            # Create a new connection for this thread
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.vhost,
                credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Declare queue (passive to check existence)
            channel.queue_declare(queue=queue_name, passive=False, durable=True)
            
            def callback(ch, method, properties, body):
                """Message callback"""
                try:
                    message = json.loads(body.decode())
                    self.captured_messages[queue_name].append({
                        "routing_key": method.routing_key,
                        "body": message,
                        "properties": {
                            "content_type": properties.content_type,
                            "delivery_mode": properties.delivery_mode,
                            "timestamp": properties.timestamp,
                        }
                    })
                    logger.debug(f"📨 Captured message from {queue_name}: {message}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)
            
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"🎧 Consumer started for queue: {queue_name}")
            
            # Consume messages until stop flag is set
            while not self.stop_flags[queue_name].is_set():
                connection.process_data_events(time_limit=1)
            
            channel.close()
            connection.close()
            logger.info(f"🛑 Consumer stopped for queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"❌ Consumer error for {queue_name}: {e}")
    
    def stop_monitoring(self, queue_name: str):
        """
        Stop monitoring a queue.
        
        Args:
            queue_name: Queue to stop monitoring
        """
        if queue_name not in self.consumer_threads:
            logger.warning(f"⚠️ Not monitoring queue: {queue_name}")
            return
        
        self.stop_flags[queue_name].set()
        self.consumer_threads[queue_name].join(timeout=5)
        
        del self.consumer_threads[queue_name]
        del self.stop_flags[queue_name]
        
        logger.info(f"🛑 Stopped monitoring queue: {queue_name}")
    
    def get_messages(self, queue_name: str) -> List[Dict[str, Any]]:
        """
        Get all captured messages from a queue.
        
        Args:
            queue_name: Queue name
        
        Returns:
            List of captured messages
        """
        return self.captured_messages.get(queue_name, [])
    
    def wait_for_message(
        self,
        queue_name: str,
        filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Wait for a message matching the filter function.
        
        Args:
            queue_name: Queue to monitor
            filter_func: Optional function to filter messages
            timeout: Timeout in seconds
        
        Returns:
            The matching message
        
        Raises:
            TimeoutError: If no matching message found within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages(queue_name)
            
            for message in messages:
                if filter_func is None or filter_func(message):
                    logger.info(f"✅ Found matching message in {queue_name}")
                    return message
            
            time.sleep(0.5)
        
        raise TimeoutError(
            f"❌ No matching message found in {queue_name} within {timeout} seconds"
        )
    
    def assert_message_published(
        self,
        queue_name: str,
        expected_body: Dict[str, Any],
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Assert that a message with specific content was published.
        
        Args:
            queue_name: Queue to check
            expected_body: Expected message body (partial match)
            timeout: Timeout in seconds
        
        Returns:
            The matching message
        
        Raises:
            AssertionError: If message not found
        """
        def filter_func(message: Dict[str, Any]) -> bool:
            body = message.get("body", {})
            return all(body.get(k) == v for k, v in expected_body.items())
        
        try:
            message = self.wait_for_message(queue_name, filter_func, timeout)
            logger.info(f"✅ Message assertion passed for {queue_name}")
            return message
        except TimeoutError:
            raise AssertionError(
                f"❌ Expected message not found in {queue_name}: {expected_body}"
            )
    
    def assert_message_count(self, queue_name: str, expected_count: int) -> int:
        """
        Assert that the number of captured messages matches expected count.
        
        Args:
            queue_name: Queue to check
            expected_count: Expected number of messages
        
        Returns:
            Actual count
        
        Raises:
            AssertionError: If count doesn't match
        """
        actual_count = len(self.get_messages(queue_name))
        
        if actual_count != expected_count:
            raise AssertionError(
                f"❌ Message count mismatch in {queue_name}: expected {expected_count}, got {actual_count}"
            )
        
        logger.info(f"✅ Message count matches: {actual_count} in {queue_name}")
        return actual_count
    
    def clear_messages(self, queue_name: str):
        """Clear captured messages for a queue"""
        self.captured_messages[queue_name] = []
        logger.debug(f"🧹 Cleared messages for {queue_name}")
    
    def close(self):
        """Stop all consumers and close connections"""
        for queue_name in list(self.consumer_threads.keys()):
            self.stop_monitoring(queue_name)
        
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        
        logger.info("🔌 Queue monitor closed")
