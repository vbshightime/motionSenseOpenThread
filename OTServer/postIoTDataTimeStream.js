'use strict';
const AWS = require('aws-sdk');
AWS.config.update({region: 'ap-south-1'});
const util = require('./util');
var https = require('https');
const { Console } = require('console');

var agent = new https.Agent({
  maxSockets: util.SOCKET
});

const writeClient = new AWS.TimestreamWrite({
  region:'us-east-1',
  maxRetries: util.MAX_RETRY,
  httpOptions: {
    timeout: util.TIMEOUT,
    agent: agent
}
})

exports.handler = async (event) => {
  //console.log(event);
  try{
    let Items = event;
    for (let i = 0; i <= (Items.Data.length)-1; i++) {        
      let item = Items.Data[i];
      const unixTime = (Date.parse(item.timestamp))-19800000;
      console.log(unixTime);
      if (!isNaN(unixTime)) {
        let record = prepare_record((unixTime))
        /*record['MeasureValues'].push(prepare_measure('Accelx',item.Accelx))
        record['MeasureValues'].push(prepare_measure('Accely',item.Accely))
        record['MeasureValues'].push(prepare_measure('Accelz',item.Accelz))*/
        record.push(prepare_measure('Accelx',item.Accelx))
        record.push(prepare_measure('Accely',item.Accely))
        record.push(prepare_measure('Accelz',item.Accelz))
        //const records = [record];
        await writeRecords(record,prepare_common_attributes(item.device_id,(unixTime)));  
      }else{
        console.log("mot a number");
      }
      
    }
    
}catch(err){
    console.log("Error",err);
}
}


const writeRecords = async(devicePayload,common)=>{
  console.log(devicePayload)
  console.log(common)
  
  const params = {
        DatabaseName: util.DATABASE_NAME,
        TableName: util.TABLE_NAME,
        Records: devicePayload,
        CommonAttributes: common
    };
  console.log(params)
  const request = writeClient.writeRecords(params);
  await request.promise().then(
    (data) => {
      console.log("Write records successful",data);
  },
  (err) => {
      console.log("Error writing records:", err);
      if (err.code === 'RejectedRecordsException') {
          const responsePayload = JSON.parse(request.response.httpResponse.body.toString());
          console.log("RejectedRecords: ", responsePayload.RejectedRecords);
          console.log("Other records were written successfully. ");
      }
  }
);
}

let prepare_common_attributes = (deviceId,unixTime)=>{
  //const common_attributes = {'Dimensions':[{'Name': 'device_id', 'Value': `${deviceId}`}],'MeasureName':'motion','MeasureValueType':'MULTI','Time': `${unixTime}`, 'TimeUnit': 'MILLISECONDS'};
  const common_attributes = {'Dimensions':[{'Name': 'device_id', 'Value': `${deviceId}`}],'MeasureValueType':'DOUBLE','Time': `${unixTime}`, 'TimeUnit': 'MILLISECONDS'};
  return common_attributes;
}

/*let prepare_measure = (measure_name,measure_value)=>{
  const measure = {
    'Name': measure_name,
    'Value': `${measure_value}`,
    'Type': 'DOUBLE'
  };
  return measure;
}*/

let prepare_measure = (measure_name,measure_value)=>{
  const measure = {
    'MeasureName': measure_name,
    'MeasureValue': `${measure_value}`,
  };
  return measure;
}

/*let prepare_record = (timestamp)=>{
  //const unixTime = Date.parse(timestamp);
  let record = {
    //'Time': `${unixTime}`,
    'MeasureValues': []
    };
    return record;
}*/

let prepare_record = (timestamp)=>{
  //const unixTime = Date.parse(timestamp);
  let record = []
    return record;
}


