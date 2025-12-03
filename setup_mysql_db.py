# ============================================================================
# MySQL DATABASE SETUP SCRIPT
# ============================================================================

import mysql.connector
import pandas as pd
from mysql.connector import Error

def create_database_and_table():
    '''
    Create MySQL database and table for credit card data
    '''
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Update with your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS credit_cards")
            print("✓ Database 'credit_cards' created")

            # Use the database
            cursor.execute("USE credit_cards")

            # Create table
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS customer_data (
                Customer_ID VARCHAR(20) PRIMARY KEY,
                Credit_Limit INT,
                Utilisation_Percent FLOAT,
                Avg_Payment_Ratio FLOAT,
                Min_Due_Paid_Frequency FLOAT,
                Merchant_Mix_Index FLOAT,
                Cash_Withdrawal_Percent FLOAT,
                Recent_Spend_Change_Percent FLOAT,
                DPD_Bucket_Next_Month INT,
                Risk_Score FLOAT DEFAULT NULL,
                Risk_Level VARCHAR(20) DEFAULT NULL,
                Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            '''

            cursor.execute(create_table_query)
            print("✓ Table 'customer_data' created")

            connection.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ MySQL connection closed")

def load_sample_data_to_mysql():
    '''
    Load sample CSV data into MySQL database
    '''
    try:
        # Read CSV
        df = pd.read_csv('sample_data.csv')

        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update with your MySQL password
            database='credit_cards'
        )

        cursor = connection.cursor()

        # Insert data
        for index, row in df.iterrows():
            insert_query = '''
            INSERT INTO customer_data 
            (Customer_ID, Credit_Limit, Utilisation_Percent, Avg_Payment_Ratio,
             Min_Due_Paid_Frequency, Merchant_Mix_Index, Cash_Withdrawal_Percent,
             Recent_Spend_Change_Percent, DPD_Bucket_Next_Month)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            Credit_Limit = VALUES(Credit_Limit),
            Utilisation_Percent = VALUES(Utilisation_Percent)
            '''

            values = (
                row['Customer_ID'],
                int(row['Credit_Limit']),
                float(row['Utilisation_%']),
                float(row['Avg_Payment_Ratio']),
                float(row['Min_Due_Paid_Frequency']),
                float(row['Merchant_Mix_Index']),
                float(row['Cash_Withdrawal_%']),
                float(row['Recent_Spend_Change_%']),
                int(row['DPD_Bucket_Next_Month'])
            )

            cursor.execute(insert_query, values)

        connection.commit()
        print(f"✓ {len(df)} records loaded into MySQL database")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("=" * 80)
    print("MySQL DATABASE SETUP")
    print("=" * 80)

    # Step 1: Create database and table
    create_database_and_table()

    print()

    # Step 2: Load sample data
    load_sample_data_to_mysql()

    print("=" * 80)
    print("✓ DATABASE SETUP COMPLETE")
    print("=" * 80)
