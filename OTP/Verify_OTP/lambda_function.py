import json
from datetime import datetime
from DB_manager import DatabaseManager

# ---------------- LAMBDA HANDLER ----------------
def lambda_handler(event, context):
    connection = None
    cursor = None

    try:
        body = json.loads(event.get("body", "{}"))
        mobile = body.get("mobile")
        otp = body.get("otp")

        if not mobile or not otp:
            return response(400, "Mobile and OTP are required")

        # DB connection
        connection = DatabaseManager.get_db_connection()
        cursor = connection.cursor()

        # Fetch OTP details
        cursor.execute("""
            SELECT userId, otp, otp_expiry
            FROM USERS
            WHERE mobile = %s
        """, (mobile,))
        user = cursor.fetchone()

        if not user:
            return response(404, "User not found")

        if user["otp"] != otp:
            return response(400, "Invalid OTP")

        if datetime.now() > user["otp_expiry"]:
            return response(400, "OTP expired")

        # OTP verified successfully
        cursor.execute("""
            UPDATE USERS
            SET is_verified = 1,
                otp = NULL,
                otp_expiry = NULL
            WHERE mobile = %s
        """, (mobile,))

        connection.commit()

        return response(200, "OTP verified successfully")

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
            "mobile": "9876543211",
            "otp": "381920"
        })
    }

    result = lambda_handler(test_event, None)
    print("Local Test Output:")
    print(json.dumps(result, indent=4))
