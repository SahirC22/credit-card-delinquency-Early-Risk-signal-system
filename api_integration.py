# ============================================================================
# LIVE SERVER / API INTEGRATION MODULE
# ============================================================================

import requests
import pandas as pd
import json

class DataAPIClient:
    '''
    Client for integrating with live data APIs
    '''

    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}' if api_key else ''
        }

    def fetch_customer_data(self, endpoint='/api/customers', params=None):
        '''
        Fetch customer data from API endpoint
        '''
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                return df
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def post_risk_scores(self, risk_data, endpoint='/api/risk-scores'):
        '''
        Post risk assessment results back to API
        '''
        try:
            url = f"{self.base_url}{endpoint}"
            payload = risk_data.to_dict('records')

            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code in [200, 201]:
                print("✓ Risk scores updated successfully")
                return True
            else:
                print(f"API Error: {response.status_code}")
                return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

# EXAMPLE USAGE
if __name__ == "__main__":
    # Initialize API client
    api_client = DataAPIClient(
        base_url="https://your-api-server.com",
        api_key="your-api-key-here"
    )

    # Fetch data
    df = api_client.fetch_customer_data()

    if df is not None:
        print(f"✓ Fetched {len(df)} records from API")
