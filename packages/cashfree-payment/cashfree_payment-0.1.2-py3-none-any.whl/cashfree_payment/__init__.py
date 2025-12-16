import requests
import json
import uuid
import os
import bcrypt
from datetime import datetime

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    psycopg2 = None

__version__ = "0.1.2"
__all__ = [
    "pay",
    "create_owner",
    "owner_login",
    "generate_access_key",
    "generate_access_key_custom",
    "list_keys",
    "ban_key",
    "unban_key",
    "delete_key",
    "update_key_expiry",
    "validate_access_key",
    "deactivate_key",
]


def _is_api_mode():
    return os.environ.get('CASHFREE_API_URL') is not None


def _get_api_url():
    return os.environ.get('CASHFREE_API_URL', '').rstrip('/')


def get_db_connection():
    if _is_api_mode():
        raise RuntimeError("Database not available in API mode. Use owner mode with NEON_DATABASE_URL.")
    if not HAS_PSYCOPG2:
        raise ImportError(
            "psycopg2 is required for database features. "
            "Install it with: pip install cashfree-payment[postgres]"
        )
    db_url = os.environ.get('NEON_DATABASE_URL')
    if not db_url:
        raise RuntimeError("NEON_DATABASE_URL environment variable not set")
    return psycopg2.connect(db_url)


def get_user_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json().get('ip')
    except:
        return None


def get_cookie_from_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT cookie FROM cookies ORDER BY id DESC LIMIT 1')
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def create_owner(username, password):
    if _is_api_mode():
        raise RuntimeError("create_owner is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cur.execute(
            'INSERT INTO owners (username, password_hash) VALUES (%s, %s) RETURNING id',
            (username, password_hash)
        )
        owner_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        print(f"Owner created: {username}")
        return owner_id
    except Exception as e:
        conn.close()
        print(f"Error creating owner: {e}")
        return None


def owner_login(username, password):
    if _is_api_mode():
        raise RuntimeError("owner_login is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, password_hash FROM owners WHERE username = %s', (username,))
    row = cur.fetchone()
    conn.close()
    
    if row and bcrypt.checkpw(password.encode(), row[1].encode()):
        print(f"Login successful: {username}")
        return row[0]
    print("Login failed: Invalid username or password")
    return None


def generate_access_key(owner_id, valid_days=30, valid_hours=0):
    if _is_api_mode():
        raise RuntimeError("generate_access_key is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    
    key_value = f"KEY_{uuid.uuid4().hex}"
    
    cur.execute(
        '''INSERT INTO access_keys (key_value, owner_id, valid_until) 
           VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '%s days' + INTERVAL '%s hours') 
           RETURNING key_value, valid_until''',
        (key_value, owner_id, valid_days, valid_hours)
    )
    result = cur.fetchone()
    conn.commit()
    conn.close()
    
    print(f"Access key generated: {result[0]}")
    print(f"Valid until: {result[1]}")
    return result[0]


def validate_access_key(access_key):
    if _is_api_mode():
        api_url = _get_api_url()
        try:
            response = requests.post(
                f"{api_url}/validate",
                json={"access_key": access_key},
                timeout=10
            )
            data = response.json()
            return data.get("valid", False)
        except Exception as e:
            print(f"API error: {e}")
            return False
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        '''SELECT id, valid_until, is_active FROM access_keys 
           WHERE key_value = %s''',
        (access_key,)
    )
    row = cur.fetchone()
    conn.close()
    
    if not row:
        print("Invalid access key")
        return False
    
    key_id, valid_until, is_active = row
    
    if not is_active:
        print("Access key is deactivated")
        return False
    
    if datetime.now() > valid_until:
        print("Access key has expired")
        return False
    
    return True


def generate_access_key_custom(owner_id, valid_until_str):
    if _is_api_mode():
        raise RuntimeError("generate_access_key_custom is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    
    key_value = f"KEY_{uuid.uuid4().hex}"
    valid_until = datetime.strptime(valid_until_str, "%Y-%m-%d %H:%M:%S")
    
    cur.execute(
        '''INSERT INTO access_keys (key_value, owner_id, valid_until) 
           VALUES (%s, %s, %s) 
           RETURNING key_value, valid_until''',
        (key_value, owner_id, valid_until)
    )
    result = cur.fetchone()
    conn.commit()
    conn.close()
    
    print(f"Access key generated: {result[0]}")
    print(f"Valid until: {result[1]}")
    return result[0]


def ban_key(owner_id, access_key):
    if _is_api_mode():
        raise RuntimeError("ban_key is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE access_keys SET is_active = FALSE WHERE key_value = %s AND owner_id = %s',
        (access_key, owner_id)
    )
    conn.commit()
    conn.close()
    print(f"Key BANNED: {access_key}")


def unban_key(owner_id, access_key):
    if _is_api_mode():
        raise RuntimeError("unban_key is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE access_keys SET is_active = TRUE WHERE key_value = %s AND owner_id = %s',
        (access_key, owner_id)
    )
    conn.commit()
    conn.close()
    print(f"Key UNBANNED: {access_key}")


def delete_key(owner_id, access_key):
    if _is_api_mode():
        raise RuntimeError("delete_key is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'DELETE FROM access_keys WHERE key_value = %s AND owner_id = %s',
        (access_key, owner_id)
    )
    conn.commit()
    conn.close()
    print(f"Key DELETED: {access_key}")


def update_key_expiry(owner_id, access_key, new_valid_until_str):
    if _is_api_mode():
        raise RuntimeError("update_key_expiry is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    new_valid_until = datetime.strptime(new_valid_until_str, "%Y-%m-%d %H:%M:%S")
    cur.execute(
        'UPDATE access_keys SET valid_until = %s WHERE key_value = %s AND owner_id = %s',
        (new_valid_until, access_key, owner_id)
    )
    conn.commit()
    conn.close()
    print(f"Key expiry updated to: {new_valid_until}")


def deactivate_key(owner_id, access_key):
    if _is_api_mode():
        raise RuntimeError("deactivate_key is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE access_keys SET is_active = FALSE WHERE key_value = %s AND owner_id = %s',
        (access_key, owner_id)
    )
    conn.commit()
    conn.close()
    print(f"Key deactivated: {access_key}")


def list_keys(owner_id):
    if _is_api_mode():
        raise RuntimeError("list_keys is only available in owner mode (with database)")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT key_value, valid_until, is_active FROM access_keys WHERE owner_id = %s ORDER BY id DESC',
        (owner_id,)
    )
    rows = cur.fetchall()
    conn.close()
    
    print("\n=== Your Access Keys ===")
    for row in rows:
        status = "ACTIVE" if row[2] else "INACTIVE"
        expired = " (EXPIRED)" if datetime.now() > row[1] else ""
        print(f"Key: {row[0]} | Valid until: {row[1]} | Status: {status}{expired}")
    return rows


def get_session_for_ip(user_ip):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT id, payment_session_id, request_count FROM sessions WHERE user_ip = %s ORDER BY id DESC LIMIT 1',
        (user_ip,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_request_count(session_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE sessions SET request_count = request_count + 1 WHERE id = %s',
        (session_id,)
    )
    conn.commit()
    conn.close()


def save_session_to_db(order_id, payment_session_id, amount, upi_id, user_ip):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO sessions (order_id, payment_session_id, amount, upi_id, user_ip, request_count) VALUES (%s, %s, %s, %s, %s, %s)',
        (order_id, payment_session_id, amount, upi_id, user_ip, 1)
    )
    conn.commit()
    conn.close()


def create_new_session(upi_id, user_ip):
    url = "https://payments.cashfree.com/plpf/forms/pggrowthsvc/v1/payment-forms/bsa-pay-fees/payments"

    random_order_id = f"CFPay_bsa-pay-fees_{uuid.uuid4().hex}"
    x_chxs_id = get_cookie_from_db()

    payload = {
        "amount": "1.00",
        "form_data": [
            {"fieldId": 26451, "value": 1},
            {"fieldId": 26452, "value": "9900224210", "meta_data": {"country_code": "+91"}},
            {"fieldId": 26453, "value": "9900224210@gmail.com"},
            {"fieldId": 26455, "value": "Q"},
            {"fieldId": 26456, "value": "W"},
            {"fieldId": 26457, "value": upi_id}
        ],
        "orderPayRequestMeta": {
            "orderId": random_order_id,
            "customerId": "eb3b71d9-b344-48e0-b488-68daeda7f548",
            "source": "PForm"
        }
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Content-Type': "application/json",
        'x-request-id': "plpf-e4d83c1c-5c8b-4830-b9f9-7cb3218bcd1c",
        'x-chxs-id': x_chxs_id,
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua': "\"Android WebView\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        'sec-ch-ua-mobile': "?1",
        'origin': "https://payments.cashfree.com",
        'x-requested-with': "mark.via.gp",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://payments.cashfree.com/forms/bsa-pay-fees",
        'accept-language': "en-US,en;q=0.9",
        'priority': "u=1, i"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print("NEW SESSION CREATED")
    print("ORDER ID →", random_order_id)
    print(response.text)

    try:
        response_data = json.loads(response.text)
        payment_session_id = response_data.get('paymentSessionId')
        if payment_session_id:
            save_session_to_db(random_order_id, payment_session_id, "1.00", upi_id, user_ip)
            return payment_session_id
    except:
        pass
    return None


def pay(upi_id, access_key):
    if _is_api_mode():
        api_url = _get_api_url()
        try:
            response = requests.post(
                f"{api_url}/pay",
                json={"upi_id": upi_id, "access_key": access_key},
                timeout=30
            )
            data = response.json()
            if data.get("success"):
                print("Payment successful")
                print("SESSION ID →", data.get("session_id"))
                return data.get("session_id")
            else:
                print("Payment failed:", data.get("error", "Unknown error"))
                return None
        except Exception as e:
            print(f"API error: {e}")
            return None
    
    if not validate_access_key(access_key):
        print("ACCESS DENIED: Invalid or expired access key")
        return None
    
    print("ACCESS KEY VALID")
    
    user_ip = get_user_ip()
    print("USER IP →", user_ip)

    session_data = get_session_for_ip(user_ip)

    if session_data:
        session_id, payment_session_id, request_count = session_data
        
        if request_count < 20:
            update_request_count(session_id)
            print(f"Using existing session (Request {request_count + 1}/20)")
            print("SESSION ID →", payment_session_id)
            return payment_session_id
        else:
            print("Session expired (20 requests reached). Creating new session...")
            return create_new_session(upi_id, user_ip)
    else:
        print("No session found for this IP. Creating new session...")
        return create_new_session(upi_id, user_ip)
