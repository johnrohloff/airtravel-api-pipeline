<h1> Air Travel API Pipeline </h1>

<h2> Description </h2>
<b>This project focuses on obtaining daily airport travel data from some of the most popular Canadian airports on a daily basis by using various AWS services and displaying them using Amazon Quicksight </b>
<br></br>

- Features used:
    - <b>AWS Lambda</b> : Serverless function to grab specific data using AviationStack API focusing on the most recent flight information from specific Canadian airports. Results written to S3 in csv format.
    - <b>AviationStack API</b> : An API to grab daily air travel information
    - <b>Amazon S3</b> : Used to store the resulting csv files, directly written to by the lambda function
    - <b>Amazon EventBridge</b> : Scheduled to run the Lambda function every night at 12:00:00 UTC 
    - <b>Amazon Quicksight</b> : Used to visually represent the dataset stored in our S3 bucket.
 
  
     
