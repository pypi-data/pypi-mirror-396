import requests
import json
import socket
import time
from datetime import datetime, timedelta, timezone
from flatten_json import flatten
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient
import copy
import os 
import urllib3

MONGODB_URL = None
ESDL_HOST = None
ESDL_PORT = None
Database=None
logs_count_collection=None
error_logs_collection=None
BASE_URL =None
AUTH_TOKEN =None
webhook_url =None
JENKINS_URL=None
JENKINS_USER=None
JENKINS_API_TOKEN=None
TRIGGER_TOKEN=None


def configure_from_env():
    """Call this once from your main script AFTER load_dotenv()."""
    global MONGODB_URL, ESDL_HOST, ESDL_PORT,Database, logs_count_collection, error_logs_collection,BASE_URL,AUTH_TOKEN,webhook_url,JENKINS_URL,JENKINS_USER,JENKINS_API_TOKEN,TRIGGER_TOKEN

    MONGODB_URL = os.getenv("MONGODB_URL")
    ESDL_HOST = os.getenv("ESDL_HOST")
    
    port_value = os.getenv("ESDL_PORT")
    if port_value is None:
        raise ValueError("ESDL_PORT missing from .env")
    ESDL_PORT = int(port_value)

    Database=os.getenv('Database')
    logs_count_collection=os.getenv('logs_count_collection')
    error_logs_collection=os.getenv('error_logs_collection')
    #administrator credentials
    BASE_URL =os.getenv('BASE_URL')
    AUTH_TOKEN =os.getenv('AUTH_TOKEN')

    webhook_url =os.getenv('webhook_url')
    JENKINS_URL=os.getenv('JENKINS_URL',None)
    JENKINS_USER=os.getenv('JENKINS_USER',None)
    JENKINS_API_TOKEN=os.getenv('JENKINS_API_TOKEN',None)
    TRIGGER_TOKEN=os.getenv('TRIGGER_TOKEN', None)

def store_error_in_mongo(error_message, label_details, end_time,status_code=None):
    build_error_and_send(error_message, label_details)
    try:
        client = MongoClient(MONGODB_URL)
        db = client[Database]
        collection = db[error_logs_collection]

        rounded_time = end_time

        # Extract HTTP status code if available
        if status_code==None:
            if hasattr(error_message, 'response') and error_message.response is not None:
                try:
                    status_code = error_message.response.status_code
                except:
                    status_code = None

        # Find existing record
        existing = collection.find_one({
            "tenant":label_details.get("tenant"),
            "productName": label_details.get("productName"),
            "productModule": label_details.get("productModule", ""),
            "roundTime": rounded_time
        })

        # 🚫 RULE: If existing document already has a status code → DO NOTHING
        if existing and existing.get("statusCode") not in (None, "", "None"):
            print("Document already has statusCode. Skipping update.")
            return

        # If document exists but has NO statusCode → update statusCode + lastUpdated
        if existing:
            collection.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "statusCode": status_code,
                        "errorMessage": str(error_message),
                        "lastUpdated": datetime.now(timezone.utc)
                    }
                }
            )
            print("Updated existing document with new statusCode:", status_code)
            return

        # No document exists → insert new error document
        error_document = {
            "productName": label_details.get("productName"),
            "productModule": label_details.get("productModule", ""),
            "tenant": label_details.get("tenant", ""),
            "errorMessage": str(error_message),
            "statusCode": status_code,
            "roundTime": rounded_time,
            "lastUpdated": datetime.now(timezone.utc),
            "status": "False"
        }

        collection.insert_one(error_document)
        print("Inserted new error with statusCode:", status_code)

    except Exception as e:
        print(f"Failed to store error in MongoDB: {e}")

def process_failed_windows(label_details, api_details,run_fetch_for_time_window):
    client = MongoClient(MONGODB_URL)
    db = client[Database]
    collection = db[error_logs_collection]

    failed_docs = collection.find({
    "tenant": label_details.get("tenant"),
    "productName": label_details["productName"],
    "productModule": label_details["productModule"],
    "status": "False",
    "statusCode": {"$nin": [401, 403]}
    })

    for doc in failed_docs:
        end_time = doc["roundTime"]
        statusCode=doc["statusCode"]
        if statusCode not in (403, 401):
            try:
                print(f"running failed cases for {end_time}")
                run_fetch_for_time_window(end_time,label_details, api_details)
                collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"status": "Success"}}
                )
            except Exception as error:
                store_error_in_mongo(error, label_details, end_time)

def logs_count(label_details, Updated_count_dict):
    tenant = label_details.get("tenant")
    productName = label_details.get("productName")  # e.g. aws_waf
    
    client = MongoClient(MONGODB_URL)
    db = client[Database]
    collection = db[logs_count_collection]

    # Read existing record
    document = collection.find_one({"tenant": tenant,"date":str(datetime.now().date())})

    # If tenant exists
    if document:
        old_product_modules = document.get(productName, {})  # existing {network: 120}

        update_dict = {}

        # Loop through all modules you want to update
        for productModule, new_count in Updated_count_dict.items():

            # Read old count (0 if not exists)
            old_count = old_product_modules.get(productModule, 0)

            # Add new count
            final_count = old_count + new_count

            # Build dotted path: aws_waf.network 
            field_path = f"{productName}.{productModule}"

            # Add to update dictionary
            update_dict[field_path] = final_count

        # Update all modules in one DB call
        collection.update_one(
            {"tenant": tenant,"date":str(datetime.now().date())},
            {"$set": update_dict},
            upsert=True
        )

    else:
        # If tenant doesn't exist → insert new nested structure
        collection.insert_one({
            "tenant": tenant,
            "date":str(datetime.now().date()),
            productName: Updated_count_dict
        })

def update_count(data,label_details,updated_count_dict):
    # productName=data["productName"]

    if data.get('logType') == "EsdlProductError":
        productModule="error"
    else:
        productModule = data.get('productModule','error')   # e.g. "network"

    # Read the old count (0 if does not exist)
    productModule_count = updated_count_dict.get(productModule, 0)

    # Add 1
    productModule_count += 1

    # Update using the actual module name, NOT string "productModule"
    updated_count_dict[productModule] = productModule_count

def trigger_jenkins_job():
    params = {
        "token": TRIGGER_TOKEN,
        "cause": "Restarted after script error"
    }
    try:
        response = requests.post(
            JENKINS_URL,
            auth=(JENKINS_USER, JENKINS_API_TOKEN),
            params=params,
            timeout=10
        )

        if response.status_code == 201:
            print("✅ Jenkins job triggered successfully!")
            message="Jenkins job triggered successfully!"
            send_teams_message(message)
        else:
            print(f"⚠️ Jenkins trigger failed: {response.status_code} - {response.text}")
            message=f" Jenkins trigger failed: {response.status_code} - {response.text}"
            send_teams_message(message)
            
    except Exception as e:
        print(f"❌ Error contacting Jenkins: {e}")

def send_teams_message(error, label_details=None):
    
    payload = {
        "text": f"Error Description: {error}"  
    }
    if label_details:
        try:
            details_str = json.dumps(label_details, indent=4)
            payload["text"] += f"\nDetails: {details_str}"
        except Exception as e:
            print(f"Error serializing label_details: {e}")
            payload["text"] += "\nDetails: Unable to serialize label details."

    json_payload = json.dumps(payload)
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(webhook_url, data=json_payload, headers=headers)
        response.raise_for_status()
        print("Message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

def round_time(round_to_minutes):
    dt = datetime.now(timezone.utc)
    round_to = round_to_minutes * 60
    seconds = (dt - dt.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    rounding = (seconds // round_to) * round_to
    rounded_dt = dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=rounding)
    return rounded_dt

def is_socket_connected(sock):
    """Check if socket is still connected."""
    if not sock:
        return False
    try:
        # This will check if the socket is still connected
        sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        return True
    except:
        return False

def send_data_to_esdl(data, label_details, max_retries=5):
    """Send data to ESDL with retry logic and new connection if needed."""
    for attempt in range(max_retries):
        tcp_socket = None
        try:
            # Create new socket for each attempt
            tcp_socket = create_socket_with_retry(max_retries=5)
            if not tcp_socket:
                raise Exception("Failed to create socket connection")
            
            flat_json = flatten(data)
            json_data = json.dumps(flat_json)
            print(json_data)
            # Add newline delimiter for proper message framing
            message = json_data + '\n'
            tcp_socket.sendall(message.encode())      
            tcp_socket.close()
            return True 
            
        except Exception as e:
            print(f"Send attempt {attempt + 1} failed: {e}")
            if tcp_socket:
                try:
                    tcp_socket.close()
                except:
                    pass
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                error = f"Failed to send data after {max_retries} attempts: {e}"
                send_teams_message(error, label_details)
                logs_count(label_details, {"TCP_error":1})
                return False
    return False
    
def build_error_and_send(error, label_details):
    send_teams_message(error, label_details)
    error_details = {}
    error_details.update(label_details)
    error_details["logType"] = "EsdlProductError"
    error_details["errorDescription"] = error
    
    # Send error details with retry
    send_data_to_esdl(error_details,label_details)

def add_label(data, label_details):
    data.update(label_details)
    return data

def create_socket_with_retry(max_retries=10):
    """Create socket connection with retry logic."""
    for attempt in range(max_retries):
        tcp_socket = None
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.settimeout(30)  # 30 second timeout
            
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            tcp_socket.connect((ESDL_HOST, ESDL_PORT))
            return tcp_socket
            
        except Exception as e:
            if tcp_socket:
                try:
                    tcp_socket.close()
                except:
                    pass   
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None   
    return None

def get_integration_by_product(product_name=None, services=None, product_id=None,
                              product_type=None, customer_status="active",
                              integration_status="active", exact_match=True):
    
    # BASE_URL =os.getenv('BASE_URL')
    # AUTH_TOKEN =os.getenv('AUTH_TOKEN')

    HEADERS = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    if not product_name and not product_id:
        return {"error": "Either product_name or product_id must be provided"}
    
    endpoint = f"{BASE_URL}/api/integration-data/product"
    
    params = {}
    if product_name:
        params['product_name'] = product_name
    if product_id:
        params['product_id'] = product_id
    if product_type:
        params['product_type'] = product_type
    if customer_status is not None:
        params['customer_status'] = str(customer_status).lower()
    if integration_status is not None:
        params['integration_status'] = str(integration_status).lower()
    if services:
        params['services'] = services
    if not exact_match:
        params['exact_match'] = 'false'
    
    try:
        response = requests.get(endpoint, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error = f"Error fetching product integration data: {e} for {product_name}"
        send_teams_message(error)
        return {"error": str(e)}


def Get_tenant_details(cust_dict,fetch_logs,get_integration_data,product_name=None):
    with ThreadPoolExecutor(max_workers=min(len(cust_dict), 10)) as executor:  # Limit max workers
        futures = []
        
        for tenant, tenant_details in cust_dict.items():
            label_details = {}
            label_details["tenant"] = tenant
            label_details["L0"] = tenant_details.get("L0_uuid")
            label_details["L1"] = tenant_details.get("L1_uuid")
            label_details["L2"] = tenant_details.get("L2_uuid")
            label_details["L3"] = tenant_details.get("L3_uuid")
            tags=tenant_details["tags"]
            label_details.update(tags)

            account_details=tenant_details["accounts"]
            for Account_detail in account_details:
                api_details = get_integration_data(Account_detail, label_details)
                if api_details:
                    thread_label = copy.deepcopy(label_details)
                    futures.append(executor.submit(fetch_logs, thread_label, api_details))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                error = f"Task generated an exception: {exc} for {product_name} "
                send_teams_message(error)
        