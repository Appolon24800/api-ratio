import urllib.request
import urllib.error
import os
import json
import logging
from typing import Dict, Any

from util import default_user_agent, parse_bytes, MissingCredentialsError, ScrappingError

logger = logging.getLogger(__name__)

USER_STATS_URL = "https://redacted.sh/ajax.php?action=index"


async def get_stats(_: bool) -> Dict[str, Any]:
    try:
        res: Dict[str, Any] = {"ratio": "N/A", "upload": "N/A", "download": "N/A"}

        token = os.getenv("RED_APIKEY")
        if not token:
            raise MissingCredentialsError("Missing Redacted api key")

        try:
            req = urllib.request.Request(USER_STATS_URL, headers={"User-Agent": default_user_agent, "Authorization": token})
            with urllib.request.urlopen(req) as response:
                api_data = json.loads(response.read())
            
        except urllib.error.HTTPError as e:
            raise ScrappingError(f"Failed to get Redacted stats: HTTP {e.code}, Reason {e.reason}")
        except urllib.error.URLError as e:
            raise ScrappingError(e)

        status = api_data.get("status", "0")
        if status != "success":
            raise ScrappingError(api_data.get("error", f"Scrapping error from redacted '{api_data}'"))

        api_response = api_data.get("response", "0")
        userstats = api_response["userstats"]

        res["raw_upload"] = userstats["uploaded"]
        res["raw_download"] = userstats["downloaded"]
        #res["ratio"] = userstats["ratio"]
        res["bonus"] = 0 # No bonus system on redacted

        return res

    except (MissingCredentialsError, ScrappingError):
        raise
    except Exception as e:
        raise ScrappingError(e)
