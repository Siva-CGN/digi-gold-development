
import json
from DB_manager import DatabaseManager

# ---------------- LAMBDA HANDLER ----------------
def lambda_handler(event, context):
    connection = None
    cursor = None

    try:
        # userId from queryStringParameters (API Gateway)
        userId = None
        if event.get("queryStringParameters"):
            userId = event["queryStringParameters"].get("userId")

        # fallback for local testing
        if not userId:
            body = json.loads(event.get("body", "{}"))
            userId = body.get("userId")

        if not userId:
            return response(400, "userId is required")

        connection = DatabaseManager.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                userId,
                status,
                remarks,
                createdAt,
                updatedAt
            FROM USER_KYC
            WHERE userId = %s
        """, (userId,))
        kyc = cursor.fetchone()

        if not kyc:
            return response(404, "KYC details not found")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "userId": kyc["userId"],
                "kycStatus": kyc["status"],
                "remarks": kyc["remarks"],
                "createdAt": str(kyc["createdAt"]),
                "updatedAt": str(kyc["updatedAt"])
            })
        }

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
        "queryStringParameters": {
            "userId": "1"
        }
    }

    result = lambda_handler(test_event, None)
    print("Local Test Output:")
    print(json.dumps(result, indent=4))
