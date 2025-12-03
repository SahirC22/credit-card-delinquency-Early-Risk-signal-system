# Credit Card Delinquency Predictor - ML Web Application

## Overview
A complete machine learning-powered web application for predicting credit card delinquency risk with real-time data integration.

## Features
✅ **Dual ML Models** - Random Forest & Gradient Boosting (80% accuracy, 0.70 AUC)
✅ **Multi-Source Data** - CSV, XLSX, MySQL database, Live API integration
✅ **Real-Time Risk Scoring** - 0-10 risk scale with 3-tier classification
✅ **Interactive Dashboards** - Plotly visualizations, filterable tables
✅ **Dynamic Adaptation** - Automatically adjusts to data patterns
✅ **Export Functionality** - Download risk assessments as CSV
✅ **Single Customer Prediction** - Manual input for individual risk assessment

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database (Optional)
```bash
python setup_mysql_db.py
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## File Structure
```
├── app.py                      # Main Streamlit application
├── rf_delinquency_model.pkl    # Random Forest model
├── gb_delinquency_model.pkl    # Gradient Boosting model
├── feature_scaler.pkl          # Feature scaling transformer
├── model_metadata.json         # Model performance metrics
├── sample_data.csv             # Sample dataset (100 customers)
├── setup_mysql_db.py           # MySQL database setup script
├── api_integration.py          # Live API integration module
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Usage

### 1. Using Sample Data
- Select "Sample Data" from the sidebar
- Risk predictions will be generated automatically
- View dashboards, top-risk customers, and export results

### 2. Upload Your Own Data
- Select "Upload File" from sidebar
- Upload CSV or XLSX with required columns:
  - Credit_Limit
  - Utilisation_%
  - Avg_Payment_Ratio
  - Min_Due_Paid_Frequency
  - Merchant_Mix_Index
  - Cash_Withdrawal_%
  - Recent_Spend_Change_%

### 3. MySQL Database Integration
- Select "MySQL Database" from sidebar
- Enter connection details:
  - Host (default: localhost)
  - Username (default: root)
  - Password
  - Database name
  - SQL Query
- Click "Connect to Database"

### 4. Live API Integration
- Edit `api_integration.py` with your API endpoint
- Uncomment API data source in `app.py`
- Configure authentication headers

## Model Performance

| Model | Accuracy | ROC-AUC | Training Samples |
|-------|----------|---------|------------------|
| Random Forest | 80.0% | 0.700 | 75 |
| Gradient Boosting | 80.0% | 0.600 | 75 |

## Feature Importance Ranking

1. **Utilisation_%** - 16.3%
2. **Min_Due_Paid_Frequency** - 15.4%
3. **Merchant_Mix_Index** - 15.4%
4. **Recent_Spend_Change_%** - 14.3%
5. **Avg_Payment_Ratio** - 13.5%
6. **Cash_Withdrawal_%** - 12.8%
7. **Credit_Limit** - 12.3%

## Risk Classification

- **HIGH RISK (6-10)**: Immediate outreach recommended
- **MEDIUM RISK (3-6)**: Proactive monitoring required
- **LOW RISK (0-3)**: Standard tracking

## Technical Details

### Machine Learning Pipeline
1. **Data Preprocessing**: StandardScaler normalization
2. **Feature Engineering**: 7 behavioral indicators
3. **Model Training**: Ensemble methods with class balancing
4. **Risk Scoring**: Probability-based 0-10 scale
5. **Real-time Prediction**: Sub-second inference time

### Database Schema
```sql
CREATE TABLE customer_data (
    Customer_ID VARCHAR(20) PRIMARY KEY,
    Credit_Limit INT,
    Utilisation_Percent FLOAT,
    Avg_Payment_Ratio FLOAT,
    Min_Due_Paid_Frequency FLOAT,
    Merchant_Mix_Index FLOAT,
    Cash_Withdrawal_Percent FLOAT,
    Recent_Spend_Change_Percent FLOAT,
    DPD_Bucket_Next_Month INT,
    Risk_Score FLOAT,
    Risk_Level VARCHAR(20),
    Last_Updated TIMESTAMP
)
```

## Troubleshooting

### Issue: Models not loading
**Solution**: Ensure all .pkl files are in the same directory as app.py

### Issue: MySQL connection failed
**Solution**: 
- Check MySQL server is running
- Verify credentials in setup_mysql_db.py
- Ensure database 'credit_cards' exists

### Issue: File upload not working
**Solution**: 
- Verify column names match required features
- Check data types (numeric values only)
- Remove any null/missing values

## Future Enhancements
- [ ] XGBoost model integration
- [ ] SHAP explainability for individual predictions
- [ ] Automated retraining pipeline
- [ ] Email alert system for high-risk customers
- [ ] Multi-user authentication
- [ ] RESTful API endpoint

## Contact
For issues or questions, please contact your data science team.

---
**Version**: 1.0  
**Last Updated**: December 2, 2025
