'use strict';
const AWS = require('aws-sdk');
AWS.config.update({region: 'ap-south-1'});
const util = require('./util');
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const datatTableName = process.env.DATA_TABLE;

exports.handler = async (event) => {
  console.log(event);
  try{
    let Items = event;
    //console.log(Items.Count);
    console.log(Items.Data.length);
    console.log(Items.Data[0].device_id);
    console.log(Items.Data[(Items.Data.length)-1].device_id);
    let itemArray = [];
    for (let i = 0; i <= (Items.Data.length)-1; i++) {        
        let item = Items.Data[i]
        if(item !== null){
            let putRequest =  {PutRequest: {Item : item}};
            itemArray[i] = putRequest;
        }else{
            console.log("item is null");
            console.log(item);
        }
    }
    await updateDeviceData(itemArray) 
    return {
        statusCode: 200,
        headers: util.getResponseHeaders(),
        body: JSON.stringify({
            Success: true
        })
    };
}catch(err){
    console.log("Error",err);
    return{
        statusCode: err.statusCode ? err.statusCode : 500,
        headers: util.getResponseHeaders(),
        body: JSON.stringify({
            Success:false,
            error: err.name ? err.name : "Exception",
            //message: err.message ? err.message : "Unknown error"
        })
    }
}
}

const updateDeviceData = async(devicePayload)=>{
  let params = {
      RequestItems : {
          [datatTableName]: devicePayload
      }
  }
  console.log(params)
  await dynamoDB.batchWrite(params,(err,data)=>{
      if(err){
          return{
              statusCode: err.statusCode ? err.statusCode : 500,
              headers: util.getResponseHeaders(),
              body: JSON.stringify({
                  Success:false,
                  error: err.name ? err.name : "Exception",
                  //message: err.message ? err.message : "Unknown error"
          })  
          }
      }
  }).promise();
  return {
      statusCode: 200,
      headers: util.getResponseHeaders(),
      body: JSON.stringify({
          Success: true
      })
  };
}

