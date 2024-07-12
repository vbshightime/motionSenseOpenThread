/**
 * Route: GET /note/n/{device_id}
 */

 const AWS = require('aws-sdk');
 AWS.config.update({ region: 'ap-south-1' });
 const util = require('./util')
 const dynamoDB = new AWS.DynamoDB.DocumentClient();
const dataTableName = process.env.DATA_TABLE;

 exports.handler = async (event) => {
     try {
         let device_id = decodeURIComponent(event.pathParameters.device_id);
         console.log(device_id);
         
        let params = {
            TableName: dataTableName,
            KeyConditionExpression: "device_id = :device_id",
            ExpressionAttributeValues: {
                ":device_id": device_id
            },
            ScanIndexForward: false
        };
        let data = await dynamoDB.query(params).promise();
        if(data.Count == 0){
            return{
                statusCode: 200,
                headers: util.getResponseHeaders(),
                body: JSON.stringify({Success: false,
                                      error:"no data present"}),
            }
        }
        return {
            statusCode: 200,
            headers: util.getResponseHeaders(),
            body: JSON.stringify({Success: true,data:data})
        };
     } catch (err) {
         console.log("Error", err);
         return {
             statusCode: err.statusCode ? err.statusCode : 500,
             headers: util.getResponseHeaders(),
             body: JSON.stringify({
                 Success:false,
                 error: err.name ? err.name : "Exception",
                 message: err.message ? err.message : "Unknown error"
             })
         };
     }
 }