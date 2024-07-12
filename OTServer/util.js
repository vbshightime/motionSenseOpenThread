
const getResponseHeaders = () => {
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Origin': '*'
    }
}

const DATABASE_NAME = 'OtserverDB';
const TABLE_NAME = 'IoTSession';
const HT_TTL_HOURS = 24;
const MAX_RETRY = 10;
const SOCKET = 5000;
const TIMEOUT= 20000;
const CT_TTL_DAYS = 7;

module.exports = {
    getResponseHeaders,
    DATABASE_NAME,
    TABLE_NAME,
    HT_TTL_HOURS,
    CT_TTL_DAYS,
    MAX_RETRY,
    SOCKET,
    TIMEOUT
}