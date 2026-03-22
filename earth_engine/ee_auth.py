import ee
from google.oauth2 import service_account
from django.conf import settings


def initialize_earth_engine():
    """Initialize Earth Engine with service account credentials"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            settings.SERVICE_ACCOUNT_KEY_FILE,
            scopes=["https://www.googleapis.com/auth/earthengine"],
        )

        # Initialize Earth Engine
        ee.Initialize(credentials)
        print("✅ Earth Engine initialized successfully")

    except Exception as e:
        print(f"❌ Earth Engine initialization failed: {e}")
