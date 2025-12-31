import json
import logging
from DB_manager import DatabaseManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context=None):
    """
    DigiGold - Get All Users API
    """

    try:
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
                ORDER BY userId DESC
            """
            cursor.execute(sql)
            users = cursor.fetchall()

        connection.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Users fetched successfully",
                "count": len(users),
                "data": users
            }, default=str)
        }

    except Exception as e:
        logger.error(f"Get All Users API error: {e}")
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
    print("🔹 Running DigiGold Get All Users API – Local Test")

    test_event = {}

    response = lambda_handler(test_event)

    print("\n🔹 API Response:")
    print(json.dumps(response, indent=4))
