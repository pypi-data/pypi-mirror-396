import petl as etl
import numpy as np
from google.analytics.data_v1beta import BetaAnalyticsDataClient


class GoogleAnalytics4(object):
    """
    Class encapsulating access to GA4 reports

    Followed instructions https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart?account_type=user

    Working against the **Data API** with a **User Account**.

    1. Generated **Application Default Credentials** `gcloud auth application-default login --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/analytics.readonly"`
    2. GA admin added user to GA4
    3. Create Google cloud project at <cloud.google.com> and enable the Data API
    4. Make that the default quota project using `gcloud auth application-default set-quota-project <project-id>`    
    """

    def __init__(self):
        self.client = BetaAnalyticsDataClient()

    def run_report(self, request):
        """Runs a simple report on a Google Analytics 4 property."""
        response = self.client.run_report(request)
        header = [c.name for c in response.dimension_headers] + \
            [c.name for c in response.metric_headers]
        data = np.transpose([[c.value for c in row.dimension_values] +
                            [c.value for c in row.metric_values] for row in response.rows])

        return etl.fromcolumns(data, header=header)
