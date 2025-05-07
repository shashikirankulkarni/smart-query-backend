import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account

# Replace with your actual GA4 property ID (starts with "properties/...")
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

# Path to your service account JSON key
KEY_FILE_PATH = "app/secrets/argon-ability-459105-d3-87e87cde59a1.json"

def get_total_visits() -> int:
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
    )

    response = client.run_report(request)
    return int(response.rows[0].metric_values[0].value)