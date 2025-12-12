from __future__ import annotations

from acceldata.airflow import listener
from airflow.plugins_manager import AirflowPlugin


# os.environ["TORCH_CATALOG_URL"] = "URL of the ADOC server"
# os.environ["TORCH_ACCESS_KEY"] = "API access key generated from torch UI"
# os.environ["TORCH_SECRET_KEY"] = "API secret key generated from torch UI"
# os.environ["TORCH_CONNECTION_TIMEOUT_MS"] = "(Optional) Maximum time (in milliseconds) to wait while establishing a connection to the ADOC server. Default: 5000 ms."
# os.environ["TORCH_READ_TIMEOUT_MS"] = "(Optional) Maximum time (in milliseconds) to wait for a response from the ADOC server after a successful connection. Default: 15000 ms."

# If set matching dag ids will be ignored and everything else will be observed
# IGNORE and OBSERVE environment variables are mutually exclusive
# Don't set if OBSERVE environment variables are set in the below step
# os.environ["DAGIDS_TO_IGNORE"] = "Comma separated dag ids to ignore observation"
# os.environ["DAGIDS_REGEX_TO_IGNORE"] = "Regex for dag ids to ignore observation"

# If set matching dag ids will be observed and everything else will be ignored.
# IGNORE and OBSERVE environment variables are mutually exclusive
# Don't set if IGNORE environment variables are set in the above step
# os.environ["DAGIDS_TO_OBSERVE"] = "Comma separated dag ids to observe"
# os.environ["DAGIDS_REGEX_TO_OBSERVE"] = "Regex for dag ids to observe"


class AcceldataListenerPlugin(AirflowPlugin):
    name = "AcceldataListenerPlugin"
    listeners = [listener]
