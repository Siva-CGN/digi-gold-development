import json
import random
from datetime import datetime, timedelta
from DB_manager import DatabaseManager

# ---------------- LAMBDA HANDLER ----------------
def lambda_handler(event, context):
    connection = None
    cursor = None

    try:
        body = json.loads(event.get("body", "{}"))
        mobile = body.get("mobile")

        if not mobile:
            return response(400, "Mobile number is required")

        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.now() + timedelta(minutes=5)

        # DB connection
        connection = DatabaseManager.get_db_connection()
        cursor = connection.cursor()

        # Check user exists
        cursor.execute(
            "SELECT userId FROM USERS WHERE mobile = %s",
            (mobile,)
        )
        user = cursor.fetchone()

        if user:
            # Update OTP
            cursor.execute("""
                UPDATE USERS
                SET otp = %s,
                    otp_expiry = %s,
                    is_verified = 0
                WHERE mobile = %s
            """, (otp, otp_expiry, mobile))
        else:
            # Insert user
            cursor.execute("""
                INSERT INTO USERS (mobile, otp, otp_expiry, is_verified)
                VALUES (%s, %s, %s, 0)
            """, (mobile, otp, otp_expiry))

        connection.commit()

        # 📲 SMS integration here
        print(f"[DEBUG] OTP for {mobile} => {otp}")

        return response(200, "OTP sent successfully")

    except Exception as e:
        return response(500, str(e))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ---------------- RESPONSE BUILDER ----------------
def response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "message": message
        })
    }


# ---------------- LOCAL TEST BLOCK ----------------
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "mobile": "9876543211"
        })
    }

    result = lambda_handler(test_event, None)
    print("Local Test Output:")
    print(json.dumps(result, indent=4))
