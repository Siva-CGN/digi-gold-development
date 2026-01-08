import json
from DB_manager import DatabaseManager

# ---------------- LAMBDA HANDLER ----------------
def lambda_handler(event, context):
    connection = None
    cursor = None

    try:
        body = json.loads(event.get("body", "{}"))

        userId = body.get("userId")
        panNumber = body.get("panNumber")
        aadhaarNumber = body.get("aadhaarNumber")
        dob = body.get("dob")
        address = body.get("address")
        city = body.get("city")
        state = body.get("state")
        pincode = body.get("pincode")

        if not all([userId, panNumber, aadhaarNumber, dob]):
            return response(400, "Required KYC fields are missing")

        connection = DatabaseManager.get_db_connection()
        cursor = connection.cursor()

        # Check if KYC already exists for user
        cursor.execute("""
            SELECT kycId FROM USER_KYC WHERE userId = %s
        """, (userId,))
        kyc = cursor.fetchone()

        if kyc:
            # Update existing KYC
            cursor.execute("""
                UPDATE USER_KYC
                SET panNumber = %s,
                    aadhaarNumber = %s,
                    dob = %s,
                    address = %s,
                    city = %s,
                    state = %s,
                    pincode = %s,
                    status = 'PENDING',
                    remarks = NULL,
                    updatedAt = CURRENT_TIMESTAMP
                WHERE userId = %s
            """, (
                panNumber, aadhaarNumber, dob,
                address, city, state, pincode,
                userId
            ))
        else:
            # Insert new KYC
            cursor.execute("""
                INSERT INTO USER_KYC
                (userId, panNumber, aadhaarNumber, dob, address, city, state, pincode, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
            """, (
                userId, panNumber, aadhaarNumber, dob,
                address, city, state, pincode
            ))

        connection.commit()

        return response(200, "KYC submitted successfully")

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
            "userId": 2,
            "panNumber": "ABCDE5678F",
            "aadhaarNumber": "123412341284",
            "dob": "1998-07-15",
            "address": "1, Ram Nagar",
            "city": "Salem",
            "state": "Tamil Nadu",
            "pincode": "600001"
        })
    }

    result = lambda_handler(test_event, None)
    print("Local Test Output:")
    print(json.dumps(result, indent=4))
