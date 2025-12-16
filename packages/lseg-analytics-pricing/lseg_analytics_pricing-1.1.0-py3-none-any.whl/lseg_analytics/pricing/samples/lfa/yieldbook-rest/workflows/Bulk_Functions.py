from lseg_analytics.pricing.yield_book_rest import (
    bulk_compact_request,
    bulk_composite_request,
    BulkJsonInputItem,
    get_result,
    get_csv_bulk_result,
    get_job_status
)

import json as js

import pandas as pd
from io import StringIO

import time

compact_job_name = "J-123456"

# bulk_compact_request
compact_response = bulk_compact_request(
                    path="/bond/py",
                    name_expr='concat($.CUSIP,"_PY")',
                    body=
                        {
                            "globalSettings": 
                                { 
                                    "pricingDate": "2023-03-31" 
                                }, 
                            "input": 
                                [ 
                                    { 
                                        "identifier.$": "$.id", 
                                        "idType": "cusip", 
                                        "level.$": "$.level", 
                                        "curve": 
                                            {
                                                "curveType": "SWAP"
                                            }, 
                                        "volatility": 
                                            {
                                                "type": "Default"
                                            }
                                    }
                                ]
                        },
                    requests=
                        [
                            {
                                "id": "31418DY55", 
                                "level": "96.578"
                            }, 
                            {   
                                "id": "31418D4J8", 
                                "level": "96.131"
                            }
                        ],
                    params={},
                    create_job=True,
                    job=compact_job_name,
                    name="BulkCompactRun",
                    pri=0
                )

print("Created following requests:")

# Iterate through all request ID's
for result in compact_response.results:
    print(result.id)

# Due to async nature, code Will perform the job status check 10 times, as result is not always ready instantly, with 10 second lapse between attempts
print("Calculating please wait...\n")

attempt = 1
max_attempts = 10
all_compact_results = []
 
while attempt < max_attempts:
        
        response = get_job_status(job_ref=compact_job_name)
        ok = response.get("okCount", None)
        pending = response.get("pendingCount", None)
        running = response.get("runningCount", None)
        if running == 0 and pending == 0 and ok != 0:
            print("Job is complete!\n")
            for result in compact_response.results:
                # Request results
                singular_compact_result = get_result(request_id_parameter=result.id)
                all_compact_results.append(singular_compact_result)
            break
        else:
              # If job is not yet done, repeat the loop
              print(response)
              time.sleep(10)
              attempt += 1

# Print results
print(js.dumps(all_compact_results, indent=4))

# Due to async nature, code Will perform the job status check 10 times, as result is not always ready instantly, with 10 second lapse between attempts
print("Calculating please wait...\n")

attempt = 1
max_attempts = 10
 
while attempt < max_attempts:
        
        response = get_job_status(job_ref=compact_job_name)
        ok = response.get("okCount", None)
        pending = response.get("pendingCount", None)
        running = response.get("runningCount", None)
        if running == 0 and pending == 0 and ok != 0:
            print("Job is complete! \n")
            bulk_compact_result_csv = get_csv_bulk_result(
                                                ids=[result.id for result in compact_response.results], 
                                                fields=["CUSIP:py.cusip", "Yield:py.yield", "OAS:py.oas"]
                                            )
            break
        else:
              # If job is not yet done, repeat the loop
              print(response)
              time.sleep(10)
              attempt += 1

# Print Bulk singular result
df = pd.read_csv(StringIO(bulk_compact_result_csv))
print(df)

composite_job_name = "J-654321"

# bulk_composite_request
composite_response = bulk_composite_request(
                        requests=[
                            BulkJsonInputItem(
                                path="/bond/py",
                                body=
                                    {
                                        "globalSettings": 
                                            { 
                                                "pricingDate": "2023-03-31"
                                            },
                                        "input": 
                                            [ 
                                                {
                                                    "identifier": "31418DY55",
                                                    "idType": "cusip", 
                                                    "level": "109.706", 
                                                    "curve": 
                                                        {
                                                            "curveType": "SWAP"
                                                        }, 
                                                    "volatility": 
                                                        {
                                                            "type": "Default" 
                                                        }
                                                },                                                
                                                {
                                                    "identifier": "31418D4J8",
                                                    "idType": "cusip", 
                                                    "level": "96.131", 
                                                    "curve": 
                                                        {
                                                            "curveType": "SWAP"
                                                        }, 
                                                    "volatility": 
                                                        {
                                                            "type": "Default" 
                                                        }
                                                }
                                            ]
                                    },
                            )
                        ],
                        create_job=True,
                        job=composite_job_name
                    )

print("Created following requests:")

# Iterate through all request ID's
for result in composite_response.results:
    print(result.id)

# Due to async nature, code Will perform the job status check 10 times, as result is not always ready instantly, with 10 second lapse between attempts
print("Calculating please wait...\n")

attempt = 1
max_attempts = 10
all_composite_results = []
 
while attempt < max_attempts:
        
        response = get_job_status(job_ref=composite_job_name)
        ok = response.get("okCount", None)
        pending = response.get("pendingCount", None)
        running = response.get("runningCount", None)
        if running == 0 and pending == 0 and ok != 0:
            print("Job is complete!\n")
            for result in composite_response.results:
                # Request results
                singular_composite_result = get_result(request_id_parameter=result.id)
                all_composite_results.append(singular_composite_result)
            break
        else:
              # If job is not yet done, repeat the loop
              print(response)
              time.sleep(10)
              attempt += 1

# Print results
print(js.dumps(all_composite_results, indent=4))

# Due to async nature, code Will perform the job status check 10 times, as result is not always ready instantly, with 10 second lapse between attempts
print("Calculating please wait...\n")

attempt = 1
max_attempts = 10
all_composite_results = []
 
while attempt < max_attempts:
        
        response = get_job_status(job_ref=composite_job_name)
        ok = response.get("okCount", None)
        pending = response.get("pendingCount", None)
        running = response.get("runningCount", None)
        if running == 0 and pending == 0 and ok != 0:
            print("Job is complete!\n")
            bulk_composite_result_csv = get_csv_bulk_result(
                                                    ids=[result.id for result in composite_response.results], 
                                                    fields=["CUSIP:py.cusip", "Yield:py.yield", "OAS:py.oas"]
                                                )
            break
        else:
              # If job is not yet done, repeat the loop
              print(response)
              time.sleep(10)
              attempt += 1

# Print Bulk result
df = pd.read_csv(StringIO(bulk_composite_result_csv))
print(df)