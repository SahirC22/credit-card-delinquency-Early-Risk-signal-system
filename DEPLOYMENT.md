# DEPLOYMENT GUIDE

## Local Deployment (Development)

### Step 1: Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Application
```bash
streamlit run app.py
```

Access at: http://localhost:8501

## Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub repository
2. Go to https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file path: `app.py`
7. Click "Deploy"

**Pros**: Free, easy, automatic updates
**Cons**: Limited resources, public by default

### Option 2: Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.5" > runtime.txt

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 3: AWS EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run with nohup
nohup streamlit run app.py --server.port=8501 &

# Configure security group to allow port 8501
```

### Option 4: Docker Container

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

```bash
# Build and run
docker build -t delinquency-app .
docker run -p 8501:8501 delinquency-app
```

## Production Considerations

### 1. Environment Variables
Create `.env` file for sensitive data:
```
MYSQL_HOST=your-host
MYSQL_USER=your-user
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=credit_cards
API_KEY=your-api-key
```

Load in app:
```python
from dotenv import load_dotenv
import os
load_dotenv()
```

### 2. Database Connection Pooling
```python
from sqlalchemy.pool import QueuePool
engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. Caching & Performance
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Data loading logic
    pass
```

### 4. Error Logging
```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR
)
```

### 5. Authentication
```python
import streamlit_authenticator as stauth

# Add to app.py
authenticator = stauth.Authenticate(...)
name, authentication_status, username = authenticator.login()
```

## Monitoring & Maintenance

### Health Checks
```python
# Add endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now()}
```

### Logging
```python
# Log predictions
with open('predictions.log', 'a') as f:
    f.write(f"{timestamp},{customer_id},{risk_score}\n")
```

### Model Updates
```bash
# Retrain model periodically
python train_model.py --data new_data.csv

# Replace old model files
mv new_model.pkl rf_delinquency_model.pkl

# Restart application
streamlit run app.py
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Enable HTTPS** - Configure SSL certificates
3. **Input validation** - Sanitize all user inputs
4. **Rate limiting** - Prevent API abuse
5. **Regular updates** - Keep dependencies current

---
**Last Updated**: December 2, 2025
