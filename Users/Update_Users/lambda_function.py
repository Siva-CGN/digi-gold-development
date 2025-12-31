import json
import hashlib
import logging
from DB_manager import DatabaseManager

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context=None):
    """
    DigiGold - User Update API
    """

    try:
        logger.info(f"Event received: {event}")

        body = json.loads(event.get("body", "{}"))

        user_id = body.get("userId")
        full_name = body.get("fullName")
        email = body.get("email")
        mobile = body.get("mobile")
        password = body.get("password")
        status = body.get("status")

        if not user_id:
            return build_response(400, "userId is required")

        connection = DatabaseManager.get_db_connection()

        with connection.cursor() as cursor:

            # 🔍 Check user exists
            cursor.execute(
                "SELECT userId FROM USERS WHERE userId = %s",
                (user_id,)
            )
            existing_user = cursor.fetchone()

            if not existing_user:
                connection.close()
                return build_response(404, "User not found")

            # 🔍 Check email / mobile duplicate (if changed)
            if email or mobile:
                dup_sql = """
                    SELECT userId FROM USERS
                    WHERE (email = %s OR mobile = %s)
                      AND userId != %s
                    LIMIT 1
                """
                cursor.execute(
                    dup_sql,
                    (
                        email if email else "",
                        mobile if mobile else "",
                        user_id
                    )
                )
                duplicate = cursor.fetchone()

                if duplicate:
                    connection.close()
                    return build_response(409, "Email or mobile already in use")

            # 🧩 Build dynamic update query
            fields = []
            values = []

            if full_name:
                fields.append("fullName = %s")
                values.append(full_name)

            if email:
                fields.append("email = %s")
                values.append(email)

            if mobile:
                fields.append("mobile = %s")
                values.append(mobile)

            if password:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                fields.append("passwordHash = %s")
                values.append(password_hash)

            if status:
                fields.append("status = %s")
                values.append(status)

            if not fields:
                connection.close()
                return build_response(400, "No fields provided for update")

            fields.append("updatedAt = NOW()")

            update_sql = f"""
                UPDATE USERS
                SET {", ".join(fields)}
                WHERE userId = %s
            """

            values.append(user_id)

            cursor.execute(update_sql, tuple(values))
            connection.commit()

        connection.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "User updated successfully"
            })
        }

    except Exception as e:
        logger.error(f"User Update API error: {e}")
        return build_response(500, "Internal server error")


def build_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "message": message
        })
    }


# =====================================================
# 🔽 LOCAL TEST BLOCK (Run: python user_update.py)
# =====================================================
if __name__ == "__main__":
    print("🔹 Running DigiGold User Update API – Local Test")

    test_event = {
        "body": json.dumps({
            "userId": 1,
            "fullName": "Ravi Kumar Updated",
            "email": "ravi.updated@gmail.com",
            "mobile": "9876500000",
            "password": "123456",
            "status": "ACTIVE"
        })
    }

    response = lambda_handler(test_event)

    print("\n🔹 API Response:")
    print(json.dumps(response, indent=4))
