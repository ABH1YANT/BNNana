/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body for BNNana DDoS Detector
  *                   Target: STM32 Benchmarking (3-Layer BWN)
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "crc.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
#include "bnn_model.h"
#include "bnn_types.h"
#include "feature_order.h"
/* USER CODE END Includes */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* 
 * Request: [Header(1) | 17 Floats(68) | Checksum(1)] = 70 Bytes 
 */
#define REQ_PACKET_SIZE 70  
#define REQ_HEADER      0xAA

/* 
 * Response: [Header(1) | Pred(1) | Cycles(4) | Time_us(2) | Checksum(1)] = 9 Bytes 
 */
#define RES_PACKET_SIZE 9   
#define RES_HEADER      0x55
/* USER CODE END PD */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN PV */
uint8_t rx_buf[REQ_PACKET_SIZE];
uint8_t tx_buf[RES_PACKET_SIZE];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);

/* USER CODE BEGIN PFP */
/**
  * @brief Redirects printf to SWV (Serial Wire Viewer) ITM Console.
  * Ensure ITM Stimulus Port 0 is enabled in CubeIDE.
  */
int _write(int file, char *ptr, int len) {
    for (int i = 0; i < len; i++) {
        ITM_SendChar(*ptr++);
    }
    return len;
}

/**
  * @brief Simple 8-bit checksum calculation.
  * Matches Python: sum(data) & 0xFF
  */
uint8_t calculate_checksum(uint8_t *data, uint32_t len) {
    uint8_t sum = 0;
    for (uint32_t i = 0; i < len; i++) sum += data[i];
    return sum;
}
/* USER CODE END PFP */

/**
  * @brief  The application entry point.
  */
int main(void)
{
  /* MCU Configuration */
  HAL_Init();
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_CRC_Init();
  MX_TIM2_Init();
  MX_USART2_UART_Init();

  /* USER CODE BEGIN 2 */
  /* 1. Start Microsecond Timer (TIM2) */
  HAL_TIM_Base_Start(&htim2);

  /* 2. Enable DWT Cycle Counter for high-precision benchmarking */
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
  DWT->CYCCNT = 0;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

  /* 3. Clear UART RX Buffer to prevent startup glitches */
  __HAL_UART_FLUSH_DRREGISTER(&huart2);

  printf("\r\n====================================\r\n");
  printf("   BNNana DDoS Detector Initialized   \r\n");
  printf("   Arch: 3-Layer [16, 16, 16] BWN     \r\n");
  printf("   Debug: SWV | Data: UART2 (115200)  \r\n");
  printf("====================================\r\n");
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    uint8_t header_byte = 0;

    /* 1. Header Hunt: Wait indefinitely for the start byte (0xAA) */
    if (HAL_UART_Receive(&huart2, &header_byte, 1, HAL_MAX_DELAY) == HAL_OK)
    {
        if (header_byte == REQ_HEADER)
        {
            rx_buf[0] = header_byte;

            /* 2. Read the rest of the packet (69 bytes) with 100ms timeout */
            if (HAL_UART_Receive(&huart2, &rx_buf[1], REQ_PACKET_SIZE - 1, 100) == HAL_OK)
            {
                /* 3. Verify Checksum of the 68 feature bytes */
                uint8_t received_checksum = rx_buf[REQ_PACKET_SIZE - 1];
                uint8_t computed_checksum = calculate_checksum(&rx_buf[1], 68);

                if (computed_checksum == received_checksum)
                {
                    BNN_Input input;
                    // Copy 17 floats (68 bytes) into the BNN input structure
                    memcpy(input.array, &rx_buf[1], 68);

                    /* --- START BENCHMARK --- */
                    uint32_t start_cycles = DWT->CYCCNT;
                    uint32_t start_us = __HAL_TIM_GET_COUNTER(&htim2);

                    // Run Inference
                    uint8_t prediction = bnn_predict_label(&input.named);

                    uint32_t end_us = __HAL_TIM_GET_COUNTER(&htim2);
                    uint32_t end_cycles = DWT->CYCCNT;
                    /* --- END BENCHMARK --- */

                    uint32_t total_cycles = end_cycles - start_cycles;
                    uint16_t latency_us = (uint16_t)(end_us - start_us);

                    /* 4. SWV Diagnostic Print (Does NOT go to Python) */
                    printf("Inference: Pred=%d | Cycles=%lu | Time=%u us\r\n",
                            prediction, total_cycles, latency_us);

                    /* 5. Pack Binary Response for Python */
                    tx_buf[0] = RES_HEADER;
                    tx_buf[1] = prediction;
                    memcpy(&tx_buf[2], &total_cycles, 4); // 4 bytes (uint32_t)
                    memcpy(&tx_buf[6], &latency_us, 2);   // 2 bytes (uint16_t)
                    
                    // Checksum of [Pred + Cycles + Latency] (7 bytes)
                    tx_buf[8] = calculate_checksum(&tx_buf[1], 7);

                    /* 6. Transmit back to Python via UART */
                    HAL_UART_Transmit(&huart2, tx_buf, RES_PACKET_SIZE, 50);

                    /* Toggle LED to show activity */
                    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
                }
                else
                {
                    printf("Error: Checksum Mismatch (Exp: %02X, Got: %02X)\r\n",
                            computed_checksum, received_checksum);
                }
            }
        }
    }
  }
  /* USER CODE END WHILE */
}

/**
  * @brief System Clock Configuration
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 360;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 2;
  RCC_OscInitStruct.PLL.PLLR = 2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  if (HAL_PWREx_EnableOverDrive() != HAL_OK)
  {
    Error_Handler();
  }

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}