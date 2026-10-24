/**
 ***************************************************************************************************
 * @file glcd.h
 * @author
 * @brief Driver for the ks108 GLCD screen
 *
 ***************************************************************************************************
 */

/* Define to prevent recursive inclusion ---------------------------------------------------------*/
#ifndef GLCD_H
#define GLCD_H

/* Includes --------------------------------------------------------------------------------------*/
#include <stdint.h>

/* Exported types --------------------------------------------------------------------------------*/

/**
 * @brief Mode for the GLCD
 *
 */
typedef enum
{
    GLCD_OFF = 0, /**<  */
    GLCD_ON = 1,  /**<  */
} glcd_mode_t;

/**
 * @brief Screen side
 *
 */
typedef enum
{
    GLCD_LEFT = 0,  /**< Left */
    GLCD_RIGHT = 1, /**< Right */
} glcd_side_t;

/**
 * @brief Font size
 *
 */
typedef enum
{
    F3X6 = 0, /**< Font Size 3x6 */
    F8X8 = 1, /**< Font Size 8x8 */
} glcd_font_t;

/**
 * @brief Mode for the GLCD
 *
 */
typedef enum
{
    GLCD_BLUE = 0,  /**< Default blue color of the screen */
    GLCD_WHITE = 1, /**< White color */
} glcd_color_t;

/* Exported constants ----------------------------------------------------------------------------*/
#define GLCD_WIDTH 128 /**< GLCD screen width */
#define GLCD_HEIGHT 64 /**< GLCD screen height */

#define GLCD_CS1 LATBbits.LATB0 /**< GLCD CS1 pin */
#define GLCD_CS2 LATBbits.LATB1 /**< GLCD CS2 pin */
#define GLCD_RS LATBbits.LATB2  /**< GLCD RS pin */
#define GLCD_RW LATBbits.LATB3  /**< GLCD RW pin */
#define GLCD_E LATBbits.LATB4   /**< GLCD Enable pin */
#define GLCD_RST LATBbits.LATB5 /**< GLCD Reset pin */

#define GLCD_DATA_TRIS TRISD /**< GLCD TRIS data port */
#define WR_DATA LATD         /**< GLCD data port */
#define RD_DATA PORTD        /**< GLCD data port */

/* Exported macro --------------------------------------------------------------------------------*/

/* Exported functions ----------------------------------------------------------------------------*/

/**
 * @brief Initialize the GLCD screen
 *
 * @param mode
 */
void glcd_Init(glcd_mode_t mode);

/**
 * @brief Write a byte
 *
 * @param side GLCD_LEFT or GLCD_RIGHT
 * @param data Byte to write
 */
void glcd_WriteByte(glcd_side_t side, uint8_t data);

/**
 * @brief Read a byte
 *
 * @param side
 * @return uint8_t
 */
uint8_t glcd_ReadByte(glcd_side_t side);

/**
 * @brief Plot a specific pixel
 *
 * @param x X Position
 * @param y Y Position
 * @param color Color
 */
void glcd_PlotPixel(uint8_t x, uint8_t y, glcd_color_t color);

/**
 * @brief Set the cursor position
 *
 * @param xpos X Position
 * @param ypos Y Position
 */
void glcd_SetCursor(uint8_t xpos, uint8_t ypos);

/**
 * @brief Draw a rectangle
 *
 * @param xs X start position
 * @param ys Y start posiiton
 * @param xe X end position
 * @param ye Y end position
 * @param color Color
 */
void glcd_Rect(uint8_t xs, uint8_t ys, uint8_t xe, uint8_t ye, glcd_color_t color);

/**
 * @brief Fill the screen with a color
 *
 * @param color
 */
void glcd_FillScreen(glcd_color_t color);

/**
 * @brief Write a char with the 8x8 Font
 *
 * @param ch Character
 * @param color color
 */
void glcd_WriteChar8X8(unsigned char ch, glcd_color_t color);

/**
 * @brief Write a char with the 3x6 Font
 *
 * @param ch Character
 * @param color Color
 */
void glcd_WriteChar3x6(unsigned char ch, glcd_color_t color);

/**
 * @brief Write a string
 *
 * @param str String
 * @param len Length of str
 * @param font Size of the font
 * @param color Color
 */
void glcd_WriteString(const char str[], uint8_t len, glcd_font_t font, glcd_color_t color);

/**
 * @brief Write text
 *
 * @param str String
 * @param len Length of str
 * @param x X position
 * @param y Y position
 */
void glcd_text_write(const char str[], uint8_t len, uint8_t x, uint8_t y);

#endif /* GLCD_H */
