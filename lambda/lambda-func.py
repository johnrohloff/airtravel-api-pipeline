import csv
import json
import boto3
import os
import urllib3
from datetime import datetime

#Initialize S3 client
s3 = boto3.client('s3')

#Main Canadian Airports
locations = ["YYZ", "YVR", "YUL", "YYC", "YEG", "YOW", "YWG", "YHZ", "YQB", "YXE", "YQR", "YYT", "YYJ", "YLW", "YXU"]

#URL for the AviationStack API
BASE_URL = "http://api.aviationstack.com/v1/flights"
api_key = os.getenv("API_KEY")


#Sends out API Requests for each airport, max 1000 flights per airport collected
def fetch_flight_data():
    flight_data = []
    http = urllib3.PoolManager()
    
    for location in locations:
        #Variables for accumulating data
        offset = 0
        batch_size = 100
        max_flights = 1000

        while offset < max_flights:
            url = f"{BASE_URL}?access_key={api_key}&dep_iata={location}&limit={batch_size}&offset={offset}"
            response = http.request("GET", url)

            #Check if API request was successful
            if response.status == 200:
                data = json.loads(response.data.decode("utf-8"))
                flights = data.get("data", [])

                #No more flights
                if not flights:
                    print(f"No more flights for {location}.")
                    break 

                #Extend data + Increment
                flight_data.extend(flights)
                offset += batch_size

                if len(flights) < batch_size:
                    print(f"Last batch for {location}, received {len(flights)} flights.")
                    break 
            else:
                #Error
                print(f"Error fetching data for {location}: {response.status}")
                break 

    return flight_data


#Saves the collected data to a csv file, named by the date
def save_to_csv(data):
    #Set file name to current date
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"/tmp/flights_{timestamp}.csv"

    if not data:
        print("No data to save")
        return None

    #Extract headers from first data entry
    headers = ["flight_date", "flight_status", "departure_airport",
               "arrival_airport", "airline", "codeshare_name"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for flight in data:
            
            flight_info = flight.get("flight")
            codeshare_airline = ""

            #To grab the parent airline
            if flight_info and "codeshared" in flight_info:
                codeshare_info = flight_info["codeshared"]
                if codeshare_info:
                    codeshare_airline = codeshare_info.get("airline_name", "")

            row = [
                flight.get("flight_date", ""),
                flight.get("flight_status", ""),
                flight.get("departure", {}).get("airport", ""),
                flight.get("arrival", {}).get("airport", ""),
                flight.get("airline", {}).get("name", ""),
                codeshare_airline
            ]
            writer.writerow(row)

    return filename

#Uploads the csv to our s3 bucket specified by environment variables
def upload_to_s3(file_path):
    bucket = os.getenv("S3_BUCKET")
    if not bucket:
        raise ValueError("S3_BUCKET environment variable not set")

    filename = os.path.basename(file_path)

    with open(file_path, "rb") as file:
        s3.put_object(
            Bucket=bucket,
            Key=filename,
            Body=file,
            ContentType='text/csv'
        )

    print(f"Data saved to s3://{bucket}/{filename}")
    return filename


#Executes function with error checks
def lambda_handler(event, context):
    flights = fetch_flight_data()

    if flights:
        csv_file = save_to_csv(flights)
        if csv_file:
            s3_filename = upload_to_s3(csv_file)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Data fetched and saved successfully',
                    'filename': s3_filename,
                    'flight_count': len(flights)
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Failed to save data to CSV'})
            }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed to fetch data'})
        }