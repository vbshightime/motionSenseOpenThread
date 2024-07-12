#include "app_scheduler.h"
#include "app_timer.h"
#include "nrf_temp.h"
#include "bsp_thread.h"
#include "nrf_log_ctrl.h"
#include "nrf_log.h"
#include "nrf_log_default_backends.h"

#include "thread_coap_utils.h"
#include "thread_utils.h"
#include "mpu6050.h"

#include <openthread/instance.h>
#include <openthread/thread.h>
#include <string.h>

#define SCHED_QUEUE_SIZE      32                                                      /**< Maximum number of events in the scheduler queue. */
#define SCHED_EVENT_DATA_SIZE APP_TIMER_SCHED_EVENT_DATA_SIZE                         /**< Maximum app_scheduler event size. */
#define SENSOR_SAMPLE_RATE 1000
#define SIZE_OF_BUF 256
#define EUI64_ADDRESS_SIZE 9 

// Cow's Sensory Data
APP_TIMER_DEF(sensor_timer);
static bool  is_connected = false;
//static int32_t core_temperature   = 0;
//static int32_t counter = 0;
static int16_t AccValue[3];
static int16_t GyroValue[3];
char AcclValues[SIZE_OF_BUF];

struct Eui64Address
{
    uint8_t eui64Address[EUI64_ADDRESS_SIZE];
};

typedef struct Eui64Address Eui64Address;

static void create_sensor_payload(){  
    Eui64Address eui64;
    otPlatRadioGetIeeeEui64(thread_ot_instance_get(),eui64.eui64Address);
    char eui64Buf[9] = {0};
    sprintf(eui64Buf, "%s", (const char*)eui64.eui64Address);
    if(mpu6050_init()) // wait until MPU6050 sensor is successfully initialized
    {
        MPU6050_ReadAcc(&AccValue[0], &AccValue[1], &AccValue[2]); 
        MPU6050_ReadGyro(&GyroValue[0], &GyroValue[1], &GyroValue[2]); // Read acc value from mpu6050 internal registers and save them in the array
        snprintf(AcclValues,SIZE_OF_BUF,"{\"device_id\":\"%s\",\"Accelx\":%d,\"Accely\":%d,\"Accelz\":%d}",(const char*)eui64Buf,(int)AccValue[0],(int)AccValue[1],(int)AccValue[2]);
        
    }
}
/***************************************************************************************************
 * @section Buttons
 **************************************************************************************************/

static void bsp_event_handler(bsp_event_t event)
{
    switch (event)
    {
        case BSP_EVENT_KEY_0:
        {
            // to do
            break;
        }


        case BSP_EVENT_KEY_1:
        {
            // to do
            break;
        }

        case BSP_EVENT_KEY_3:
        {
            // to do
            break;
        }
        default:
            return;
    }
}

/***************************************************************************************************
 * @section Callbacks
 **************************************************************************************************/

static void thread_state_changed_callback(uint32_t flags, void * p_context)
{
    if (flags & OT_CHANGED_THREAD_ROLE)
    {
        switch (otThreadGetDeviceRole(p_context))
        {
            case OT_DEVICE_ROLE_CHILD:
            case OT_DEVICE_ROLE_ROUTER:
            case OT_DEVICE_ROLE_LEADER:
            {
                is_connected = true;
                APP_ERROR_CHECK(app_timer_start(sensor_timer, APP_TIMER_TICKS(SENSOR_SAMPLE_RATE), NULL));
                break;
            } 
            case OT_DEVICE_ROLE_DISABLED:
            case OT_DEVICE_ROLE_DETACHED:
            {
                is_connected = false;
                APP_ERROR_CHECK(app_timer_stop(sensor_timer));
                break;
            }
            default:
            {
                break;
            }

        }
    }

    NRF_LOG_INFO("State changed! Flags: 0x%08x Current role: %d\r\n",
                 flags,
                 otThreadGetDeviceRole(p_context));
}

/***************************************************************************************************
 * @section OTSense Callbacks
 **************************************************************************************************/
static void handler(void * p_context)
{
    (void)p_context;

    NRF_TEMP->TASKS_START = 1;
    /* Busy wait while temperature measurement is not finished. */
    while (NRF_TEMP->EVENTS_DATARDY == 0)
    {
        // Do nothing.
    }
    NRF_TEMP->EVENTS_DATARDY = 0;

    //int32_t temp = nrf_temp_read() / 4;

    NRF_TEMP->TASKS_STOP = 1;
    create_sensor_payload();
    if (is_connected)
    {
        //counter++;
        thread_coap_utils_multicast_light_request_send((const char*)AcclValues, THREAD_COAP_UTILS_MULTICAST_REALM_LOCAL);
        //thread_coap_utils_multicast_light_request_send(counter, THREAD_COAP_UTILS_MULTICAST_REALM_LOCAL);
    }
}


/***************************************************************************************************
 * @section Initialization
 **************************************************************************************************/

/**@brief Function for initializing the Thread Board Support Package
 */
static void thread_bsp_init(void)
{
    uint32_t error_code = bsp_init(BSP_INIT_LEDS | BSP_INIT_BUTTONS, bsp_event_handler);
    APP_ERROR_CHECK(error_code);

    error_code = bsp_thread_init(thread_ot_instance_get());
    APP_ERROR_CHECK(error_code);
}


/**@brief Function for initializing the Application Timer Module
 */
static void timer_init(void)
{
    uint32_t error_code = app_timer_init();
    APP_ERROR_CHECK(error_code);

    error_code = app_timer_create(&sensor_timer,
                                  APP_TIMER_MODE_REPEATED,
                                  handler);
    APP_ERROR_CHECK(error_code);
}


/**@brief Function for initializing the nrf log module.
 */
static void log_init(void)
{
    ret_code_t err_code = NRF_LOG_INIT(NULL);
    APP_ERROR_CHECK(err_code);

    NRF_LOG_DEFAULT_BACKENDS_INIT();
}


/**@brief Function for initializing the Thread Stack
 */
static void thread_instance_init(void)
{
    thread_configuration_t thread_configuration =
    {
        .radio_mode        = THREAD_RADIO_MODE_RX_ON_WHEN_IDLE,
        .autocommissioning = true,
    };

    thread_init(&thread_configuration);
    thread_cli_init();
    thread_state_changed_callback_set(thread_state_changed_callback);
}


/**@brief Function for initializing the Constrained Application Protocol Module
 */
static void thread_coap_init(void)
{
    thread_coap_utils_configuration_t thread_coap_configuration =
    {
        .coap_server_enabled               = false,
        .coap_client_enabled               = true,
        .configurable_led_blinking_enabled = false,
    };

    thread_coap_utils_init(&thread_coap_configuration);
}


/**@brief Function for initializing scheduler module.
 */
static void scheduler_init(void)
{
    APP_SCHED_INIT(SCHED_EVENT_DATA_SIZE, SCHED_QUEUE_SIZE);
}


/***************************************************************************************************
 * @section Main
 **************************************************************************************************/

int main(int argc, char * argv[])
{
    twi_init();
    log_init();
    scheduler_init();
    timer_init();
    nrf_temp_init();
    thread_instance_init();
    thread_coap_init();
    thread_bsp_init();
    while (true)
    {
        thread_process();
        app_sched_execute();

        if (NRF_LOG_PROCESS() == false)
        {
            thread_sleep();
        }
    }
}

/**
 *@}
 **/
