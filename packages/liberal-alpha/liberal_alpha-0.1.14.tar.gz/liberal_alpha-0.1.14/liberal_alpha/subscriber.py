# liberal_alpha/subscriber.py
#!/usr/bin/env python3
import asyncio
import json
import websockets
import logging
import time
import sys
from pathlib import Path
from .crypto import decrypt_alpha_message, get_wallet_address
from .utils import fetch_subscribed_records, get_user_wallet_address
from .exceptions import SubscriptionError, DecryptionError, ConfigurationError

logger = logging.getLogger(__name__)

async def subscribe_to_websocket(url: str, wallet_address: str, record_id: int, record_name: str, 
                                private_key: str = None, max_reconnect_attempts: int = 5,
                                on_message: callable = None):
    """
    Subscribe to WebSocket and handle incoming messages with decryption.
    
    Args:
        url: WebSocket URL
        wallet_address: Ethereum wallet address
        record_id: Record ID to subscribe to
        record_name: Human-readable name of the record
        private_key: Private key for decryption (optional)
        max_reconnect_attempts: Maximum number of reconnection attempts
        on_message: Optional callback function to handle received messages
    """
    reconnect_attempts = 0
    # Create a directory to store decrypted data for this record
    output_dir = Path(f"decrypted_data/record_{record_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    while reconnect_attempts < max_reconnect_attempts:
        try:
            logger.info(f"Connecting to WebSocket for record {record_id} ({record_name}) at {url}")
            
            # Connect to the WebSocket server
            async with websockets.connect(url) as websocket:
                # Send the initial connection request with wallet address and record ID
                connection_request = {"wallet_address": wallet_address, "record_id": record_id}
                logger.info(f"Sending connection request for record {record_id}: {json.dumps(connection_request)}")
                await websocket.send(json.dumps(connection_request))
                
                # Process messages
                while True:
                    try:
                        # Set a timeout to avoid blocking forever if the connection drops silently
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    except asyncio.TimeoutError:
                        # Send a ping to keep the connection alive and check if it's still active
                        try:
                            pong_waiter = await websocket.ping()
                            await asyncio.wait_for(pong_waiter, timeout=10.0)
                            logger.debug("Ping successful, connection still alive")
                            continue
                        except:
                            logger.warning("Ping failed, connection may be dead. Reconnecting...")
                            break
                    
                    try:
                        # Parse the received message as JSON
                        parsed_message = json.loads(message)
                        logger.info(f"Record {record_id} ({record_name}) received: {json.dumps(parsed_message, indent=2)}")
                        
                        # Check if this is a data message
                        if parsed_message.get("status") in ["data"]:
                            logger.info(f"Record {record_id} ({record_name}): Received encrypted data!")
                            
                            # If private key is provided, try to decrypt the data
                            if private_key and "data" in parsed_message:
                                encrypted_data = parsed_message["data"]
                                logger.info("Attempting to decrypt data with private key...")
                                
                                try:
                                    # Decrypt the data using specialized function from crypto.py
                                    decrypted_data = decrypt_alpha_message(private_key, encrypted_data)
                                    
                                    if decrypted_data:
                                        # If we have a callback function, call it with the decrypted data
                                        if on_message:
                                            on_message(decrypted_data)
                                        else:
                                            # Otherwise, print the decrypted data to the console
                                            entry_id = encrypted_data.get("entry_id", "unknown")
                                            print("\n" + "="*50)
                                            print(f"DECRYPTED DATA (Entry ID: {entry_id}):")
                                            if isinstance(decrypted_data, dict):
                                                print(json.dumps(decrypted_data, indent=2))
                                            else:
                                                print(decrypted_data)
                                            print("="*50)
                                            
                                            # Also save to a file for reference
                                            timestamp = int(time.time())
                                            filename = output_dir / f"data_{timestamp}_{entry_id}.json"
                                            with open(filename, "w") as f:
                                                if isinstance(decrypted_data, dict):
                                                    json.dump(decrypted_data, f, indent=2)
                                                else:
                                                    f.write(str(decrypted_data))
                                            logger.info(f"Saved decrypted data to {filename}")
                                    else:
                                        logger.warning("Failed to decrypt data - either not encrypted for this wallet or invalid encryption")
                                except Exception as e:
                                    logger.error(f"Error decrypting message: {e}")
                                    
                            # If no private key or decryption failed, still process the raw data
                            elif "data" in parsed_message:
                                if on_message:
                                    on_message(parsed_message["data"])
                                else:
                                    logger.info(f"Encrypted data received (no decryption):")
                                    logger.info(json.dumps(parsed_message['data'], indent=2))
                    except json.JSONDecodeError:
                        logger.warning(f"Record {record_id}: Received non-JSON message: {message}")
                        
        except websockets.exceptions.ConnectionClosed as e:
            reconnect_attempts += 1
            wait_time = min(reconnect_attempts * 2, 30)  # Exponential backoff, max 30s
            logger.error(f"WebSocket connection for record {record_id} closed: {e}. Reconnecting in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            reconnect_attempts += 1
            wait_time = min(reconnect_attempts * 2, 30)
            logger.error(f"Error in WebSocket connection for record {record_id}: {e}. Reconnecting in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    logger.error(f"Failed to maintain WebSocket connection for record {record_id} after {max_reconnect_attempts} attempts.")
    raise SubscriptionError(f"Failed to maintain connection after {max_reconnect_attempts} attempts")
    
async def main_async(api_key: str, base_url: str, wallet_address: str = None, private_key: str = None, 
                    record_id: int = None, max_reconnect: int = 5, on_message: callable = None):
    """
    Main async function to handle WebSocket subscriptions.
    
    Args:
        api_key: Liberal Alpha API key
        base_url: Backend base URL
        wallet_address: Ethereum wallet address (computed from private_key if not provided)
        private_key: Private key for decryption
        record_id: Specific record ID to subscribe to (subscribes to all if None)
        max_reconnect: Maximum number of reconnection attempts
        on_message: Optional callback function to handle received messages
    """
    # Validate required parameters
    if not api_key:
        raise ConfigurationError("API key is required for subscription")
    
    if private_key:
        logger.info("Private key provided, will attempt to decrypt messages")
        # Compute wallet_address automatically from private_key if not provided
        if not wallet_address:
            try:
                wallet_address = get_wallet_address(private_key)
                logger.info(f"Decryption wallet address: {wallet_address}")
            except Exception as e:
                raise ConfigurationError(f"Failed to derive wallet address from private key: {e}")
    
    # If a specific record ID is provided, only subscribe to that one
    if record_id:
        logger.info(f"Monitoring only record ID: {record_id}")
        records = [{"id": record_id, "name": f"Record {record_id}"}]
    else:
        # Otherwise, fetch all subscribed records from the backend
        records = fetch_subscribed_records(base_url, api_key)
        if not records:
            logger.error("No records found to monitor. Exiting.")
            raise SubscriptionError("No records found to monitor")
    
    # If wallet address is still not known, try to get it from the backend
    if not wallet_address:
        wallet_address = get_user_wallet_address(base_url, api_key)
        logger.info(f"Using wallet address: {wallet_address}")
        
    # Convert the base URL to WebSocket URL
    ws_base_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_base_url}/ws/data"
    
    # Create a task for each record to subscribe to
    tasks = []
    for record in records:
        rid = record.get("id")
        rname = record.get("name", "Unknown")
        if rid:
            logger.info(f"Setting up monitoring for record {rid} ({rname})")
            task = asyncio.create_task(subscribe_to_websocket(
                ws_url, wallet_address, rid, rname, private_key, max_reconnect, on_message
            ))
            tasks.append(task)
    
    if tasks:
        logger.info(f"Monitoring {len(tasks)} records...")
        # Use different approaches for different Python versions
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            # Cancel any remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise SubscriptionError(f"Subscription failed: {e}")
    else:
        logger.error("No valid records found to monitor. Exiting.")
        raise SubscriptionError("No valid records found to monitor")