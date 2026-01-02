import pymysql
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DatabaseManager:

    @staticmethod
    def get_db_connection():
        try:
            connection = pymysql.connect(
                host='cogni-db-dev.cp38dsvtanhf.ap-south-1.rds.amazonaws.com',
                user='admin',
                passwd='plazdb!SV',
                db='DIGIGOLD',
                connect_timeout=5,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Connected to DIGIGOLD DB")
            return connection
        except Exception as e:
            logger.error(f"DB connection error: {e}")
            raise
