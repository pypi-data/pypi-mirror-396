"""Accessors for UniProt/InterPro APIs used by post-analysis utilities.

Minimal changes applied for linting compliance without altering behaviour.
"""
import json
import ssl
import sys
from time import sleep
from urllib import request
from urllib.error import HTTPError


def pfam_domain_call(domain):
    """
    Retrieve metadata for a given Pfam domain from the InterPro API.

    Args:
        domain (str): The Pfam domain identifier to search for.

    Returns:
        dict: The metadata associated with the Pfam domain.

    Raises:
        HTTPError: If the request fails after 3 attempts, the exception is raised with the last URL attempted.

    Notes:
        - The function disables SSL verification to avoid configuration issues.
        - It retries the request up to 3 times if an HTTP 408 (Request Timeout) error occurs.
        - A short pause (0.5 seconds) is included to avoid overloading the server with requests.
    """
    # disable SSL verification to avoid config issues
    context = ssl._create_unverified_context()
    base_url = "https://www.ebi.ac.uk:443/interpro/api/entry/all/pfam/" + domain
    attempts = 0

    try:
        # create a request object with the appropriate headers
        req = request.Request(base_url, headers={"Accept": "application/json"})
        with request.urlopen(req, context=context) as res:
            # If the API times out due to a long running query, wait just over a minute
            if res.status == 408:
                sleep(61)
            elif res.status == 204:
                # if no data is found, write a message and return
                sys.stderr.write("No data found for %s\n" % domain)
                return {}

            # decode the response and store the payload
            payload = json.loads(res.read().decode())

        # Return the metadata from the payload
        return payload.get("metadata", {})

    # If an HTTPError occurs, retry the request up to 3 times before failing
    except HTTPError as e:
        if e.code == 408:
            sleep(61)
        else:
            if attempts < 3:
                attempts += 1
                sleep(61)
            else:
                sys.stderr.write("LAST URL: %s\n" % base_url)
                raise e

    sleep(0.5)  # Be nice to the server
    return {}
