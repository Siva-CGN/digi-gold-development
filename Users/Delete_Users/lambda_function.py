import json
import logging
from DB_manager import DatabaseManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context=None):
    """
    DigiGold - Delete User API (Soft Delete)
    """

    try:
        logger.info(f"Event received: {event}")

        user_id = None

        # Support query string (API Gateway)
        if event.get("queryStringParameters"):
            user_id = event["queryStringParameters"].get("userId")

        # Support body (local / POST delete)
        if not user_id and event.get("body"):
            body = json.loads(event.get("body", "{}"))
            user_id = body.get("userId")

        if not user_id:
            return build_response(400, "userId is required")

        connection = DatabaseManager.get_db_connection()

        with connection.cursor() as cursor:

            # 🔍 Check if user exists
            cursor.execute(
                "SELECT userId FROM USERS WHERE userId = %s",
                (user_id,)
            )
            user = cursor.fetchone()

            if not user:
                connection.close()
                return build_response(404, "User not found")

            # 🗑️ Soft delete (set status INACTIVE)
            delete_sql = """
                UPDATE USERS
                SET status = 'INACTIVE',
                    updatedAt = NOW()
                WHERE userId = %s
            """
            cursor.execute(delete_sql, (user_id,))
            connection.commit()

        connection.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "User deleted successfully (soft delete)"
            })
        }

    except Exception as e:
        logger.error(f"User Delete API error: {e}")
        return build_response(500, "Internal server error")


def build_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({"message": message})
    }


# =====================================================
# 🔽 LOCAL TEST BLOCK
# =====================================================
if __name__ == "__main__":
    print("🔹 Running DigiGold User Delete API – Local Test")

    test_event = {
        "body": json.dumps({
            "userId": 2
        })
    }

    response = lambda_handler(test_event)

    print("\n🔹 API Response:")
    print(json.dumps(response, indent=4))
