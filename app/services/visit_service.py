import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2 import service_account

# GA4 property ID from environment variable
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

# Local path to the JSON service account key file
KEY_FILE_PATH = "app/secrets/argon-ability-459105-d3-87e87cde59a1.json"

def get_total_visits() -> int:
    if not GA4_PROPERTY_ID:
        raise ValueError("GA4_PROPERTY_ID environment variable not set")

    credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        metrics=[Metric(name="screenPageViews")],  # Or "activeUsers" if preferred
        date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
    )

    response = client.run_report(request)
    return int(response.rows[0].metric_values[0].value)