import psycopg2

class DatabaseConnection:
    """
    Class to handle PostgreSQL database connections
    using AWS Secrets Manager credentials
    """
    
    def __init__(self):
        self.connection = None

    def connect(self, credentials):
        """Establishes database connection using credentials"""
        try:
            self.connection = psycopg2.connect(
                host=credentials['host'],
                port=credentials['port'],
                database=credentials['dbname'],
                user=credentials['username'],
                password=credentials['password'],
                connect_timeout=30
            )
        except Exception as e:
            raise Exception(f"Database connection error: {str(e)}")

    def close(self):
        """Closes the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()

    def commit_transaction(self):
        """Commits pending transactions"""
        if self.connection and not self.connection.closed:
            self.connection.commit()

    def rollback_transaction(self):
        """Rolls back pending transactions in case of error"""
        if self.connection and not self.connection.closed:
            self.connection.rollback()
