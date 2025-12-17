# utils.py
import logging
import requests
import json
import time
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)

def fetch_subscribed_records(base_url: str, api_key: str) -> list:
    """
    Fetch all data records that the user has subscribed to.
    
    Args:
        base_url: Backend base URL
        api_key: API key for authentication
        
    Returns:
        List of record objects
    """
    if not api_key:
        raise ConfigurationError("API key is required to fetch subscribed records")
        
    try:
        # First try with API key in header
        headers = {"X-API-Key": api_key}
        logger.info(f"Fetching subscriptions from {base_url}/api/subscriptions")
        
        response = requests.get(f"{base_url}/api/subscriptions", headers=headers)
        
        # If that fails with 401, try query parameter
        if response.status_code == 401:
            logger.info("API key header auth failed, trying query parameter...")
            response = requests.get(f"{base_url}/api/subscriptions?key={api_key}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract subscriptions from response (handle different response formats)
            subscriptions = []
            if "data" in data:
                if isinstance(data["data"], list):
                    subscriptions = data["data"]
                elif isinstance(data["data"], dict) and "subscriptions" in data["data"]:
                    subscriptions = data["data"]["subscriptions"]
            
            # Extract record information from subscriptions
            records = []
            for sub in subscriptions:
                if "record" in sub:
                    records.append(sub["record"])
                elif "subscription" in sub and "record" in sub:
                    records.append(sub["record"])
            
            # Also fetch the user's own records
            logger.info(f"Fetching user's own records from {base_url}/api/records")
            own_records_response = requests.get(f"{base_url}/api/records", headers=headers)
            if own_records_response.status_code == 200:
                own_data = own_records_response.json()
                if "data" in own_data:
                    # Check for data records
                    if "data_records" in own_data["data"] and isinstance(own_data["data"]["data_records"], list):
                        records.extend(own_data["data"]["data_records"])
                    # Check for alpha records
                    if "alpha_records" in own_data["data"] and isinstance(own_data["data"]["alpha_records"], list):
                        records.extend(own_data["data"]["alpha_records"])
            
            logger.info(f"Found {len(records)} records to monitor")
            return records
            
        else:
            error_msg = f"Failed to fetch subscriptions: {response.status_code}"
            if response.text:
                error_msg += f" - {response.text}"
            logger.error(error_msg)
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching subscribed records: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching subscribed records: {e}")
        return []


def get_user_wallet_address(base_url: str, api_key: str) -> str:
    """
    Get the user's wallet address using the API key.
    
    Args:
        base_url: Backend base URL
        api_key: API key for authentication
        
    Returns:
        Ethereum wallet address
    """
    if not api_key:
        raise ConfigurationError("API key is required to get wallet address")
        
    try:
        # Try to get user info using API key
        headers = {"X-API-Key": api_key}
        logger.info(f"Fetching user info from {base_url}/api/users/me")
        response = requests.get(f"{base_url}/api/users/me", headers=headers)
        
        # If that fails, try another endpoint
        if response.status_code != 200:
            logger.info("First endpoint failed, trying alternate endpoint...")
            response = requests.get(f"{base_url}/api/protected-api-key", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Different endpoints might have different response structures
            # Try to extract wallet address from various locations
            if "data" in data and "user" in data["data"] and "wallet_address" in data["data"]["user"]:
                return data["data"]["user"]["wallet_address"]
            elif "wallet_address" in data:
                return data["wallet_address"]
            elif "data" in data and "wallet_address" in data["data"]:
                return data["data"]["wallet_address"]
                
        logger.warning("Could not retrieve wallet address, using fallback method")
        # Use part of API key as fallback (this is just for identification, not actual use)
        fallback = "0x" + api_key[:40].ljust(40, '0')
        return fallback
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting wallet address: {e}")
        # Use fallback address
        fallback = "0x" + api_key[:40].ljust(40, '0')
        return fallback
    except Exception as e:
        logger.error(f"Unexpected error getting wallet address: {e}")
        # Use fallback address
        fallback = "0x" + api_key[:40].ljust(40, '0')
        return fallback


def retry_with_backoff(max_retries=5, initial_wait=1, max_wait=60):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            wait_time = initial_wait
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, ConnectionError) as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                        
                    logger.warning(f"Attempt {retries} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    
                    # Increase wait time with exponential backoff
                    wait_time = min(wait_time * 2, max_wait)
                    
        return wrapper
    return decorator


def fetch_historical_entries(base_url, api_key, record_id, page=1, page_size=10):
    """
    Fetch historical entries for a specific record.
    
    Args:
        base_url (str): The base URL of the backend API
        api_key (str): API key for authentication
        record_id (int): ID of the record to fetch history for
        page (int): Page number for pagination
        page_size (int): Number of entries per page
    
    Returns:
        dict: The historical entries data or None on error
    """
    url = f"{base_url}/api/entries/history"
    
    params = {
        "record_id": record_id,
        "page": page,
        "page_size": page_size
    }
    
    try:
        headers = {"X-API-Key": api_key}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                logger.info(f"Successfully fetched historical entries for record {record_id}")
                return data.get("data")
            else:
                logger.error(f"API error: {data.get('message')}")
                return None
        else:
            logger.error(f"Error fetching historical entries: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching historical entries: {e}")
        return None
