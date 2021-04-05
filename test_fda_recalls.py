#!/usr/bin/python3
'''
A program to list completed FDA recalls. Uses API calls to https://api.fda.gov
JSON output from the API is parsed and selected fields are written to a file in CSV format
delimited by a doulbe vertical bar '||' to avoind any confusion with embedded commas in the data

Author: John Nealy GitHub codejkn3
'''
import requests
import json
import os
import pandas as pd
import sys

OUTCSVFILE="fdarecalls.csv"
BASEAPIURL="https://api.fda.gov/food/enforcement.json"

def getRecordNumber():
    '''
    This function actually does a call with a limit of "1" so we get minmal data but the total number of records, available
    in  "meta" key portion. We use that to make the full data call later
    '''
    recordsurl = BASEAPIURL + "?limit=1&search=status.exact:Completed"
    recnum = requests.get(recordsurl)
    numdata = recnum.json()
    return(numdata.get("meta").get("results").get("total"))


def createCSVFile():

    # Make the API call and get the JSON results
    reclimit = str(getRecordNumber())
    dataurl =  BASEAPIURL + "?limit="+ reclimit + " &search=status.exact:Completed"
    r = requests.get(dataurl)
    rdata = r.json()

    try:
        with open(OUTCSVFILE,"w") as recallfile:
            # print a header line in the file
            print(f"Recall Number||Report Date||Product||Recalling Firm||Product Type||Recall Reason",file=recallfile)

            for fdaResults in rdata.get("results"): # skip the metadata and get the actual query results
                #create a tuple for the string join
                datavalues = (fdaResults.get('recall_number'),fdaResults.get('report_date'),fdaResults.get('product_description'),
                fdaResults.get('recalling_firm'),fdaResults.get('product_type'),fdaResults.get('reason_for_recall'))

                datarec = "||".join(datavalues)
                #write the record to the file
                print(datarec,file=recallfile)
    except PermissionError:
        print(f"Error writing file {OUTCSVFILE}: Permission denied.")
    except:
        print(f"Unexcpected error {sys.exc_info()[0]}")

def main():
    #Get the API data and create the CSV file
    createCSVFile()

    # the engine parameter below  is necessary in the pandas read due to the seprator being "||" and considered a regex
    # also the bars are escaped with a slash
    df = pd.read_csv("fdarecalls.csv",engine='python',sep='\|\|') 

    df= df.sort_values(by=['Report Date'],ascending=False) # sort by the report date
    print(df)


if __name__ == "__main__":
    main()
