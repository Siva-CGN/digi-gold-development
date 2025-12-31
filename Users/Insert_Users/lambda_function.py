import json
import hashlib
import logging
from DB_manager import DatabaseManager

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context=None):
    """
    DigiGold - User Registration API
    """

    try:
        logger.info(f"Event received: {event}")

        body = json.loads(event.get("body", "{}"))

        full_name = body.get("fullName")
        email = body.get("email")
        mobile = body.get("mobile")
        password = body.get("password")
        referral_code = body.get("referralCode")
        referred_by = body.get("referredBy")

        # Basic validation
        if not full_name or not email or not mobile or not password:
            return build_response(400, "Required fields are missing")

        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        connection = DatabaseManager.get_db_connection()

        with connection.cursor() as cursor:

            # 🔍 Check duplicate email or mobile
            check_sql = """
                SELECT userId FROM USERS
                WHERE email = %s OR mobile = %s
                LIMIT 1
            """
            cursor.execute(check_sql, (email, mobile))
            existing_user = cursor.fetchone()

            if existing_user:
                connection.close()
                return build_response(409, "Email or mobile already registered")

            # ➕ Insert user
            insert_sql = """
                INSERT INTO USERS (
                    fullName,
                    email,
                    mobile,
                    passwordHash,
                    referralCode,
                    referredBy,
                    status,
                    createdAt,
                    updatedAt
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', NOW(), NOW())
            """

            cursor.execute(
                insert_sql,
                (
                    full_name,
                    email,
                    mobile,
                    password_hash,
                    referral_code,
                    referred_by
                )
            )

            connection.commit()
            user_id = cursor.lastrowid

        connection.close()

        return {
            "statusCode": 201,
            "body": json.dumps({
                "message": "User registered successfully",
                "data": {
                    "userId": user_id,
                    "fullName": full_name,
                    "email": email,
                    "mobile": mobile
                }
            })
        }

    except Exception as e:
        logger.error(f"User Insert API error: {e}")
        return build_response(500, "Internal server error")


def build_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "message": message
        })
    }


# =====================================================
# 🔽 LOCAL TEST BLOCK (Run: python user_insert.py)
# =====================================================
if __name__ == "__main__":
    print("🔹 Running DigiGold User Insert API – Local Test")

    test_event = {
        "body": json.dumps({
            "fullName": "Sathish Kumar",
            "email": "sathish.kumar@gmail.com",
            "mobile": "9876543211",
            "password": "123456",
            "referralCode": "DGOLD100",
            "referredBy": "FRIEND50"
        })
    }

    response = lambda_handler(test_event)

    print("\n🔹 API Response:")
    print(json.dumps(response, indent=4))
