import json
import logging
from DB_manager import DatabaseManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context=None):
    """
    DigiGold - Get User By ID API
    """

    try:
        user_id = None

        # Support query string (API Gateway) & local test
        if event.get("queryStringParameters"):
            user_id = event["queryStringParameters"].get("userId")

        # Support body (optional)
        if not user_id and event.get("body"):
            body = json.loads(event.get("body", "{}"))
            user_id = body.get("userId")

        if not user_id:
            return build_response(400, "userId is required")

        connection = DatabaseManager.get_db_connection()

        with connection.cursor() as cursor:
            sql = """
                SELECT
                    userId,
                    fullName,
                    email,
                    mobile,
                    referralCode,
                    referredBy,
                    status,
                    createdAt,
                    updatedAt
                FROM USERS
                WHERE userId = %s
            """
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()

        connection.close()

        if not user:
            return build_response(404, "User not found")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "User fetched successfully",
                "data": user
            }, default=str)
        }

    except Exception as e:
        logger.error(f"Get User By ID API error: {e}")
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
    print("🔹 Running DigiGold Get User By ID API – Local Test")

    test_event = {
        "queryStringParameters": {
            "userId": 2
        }
    }

    response = lambda_handler(test_event)

    print("\n🔹 API Response:")
    print(json.dumps(response, indent=4))
