/**
 ***************************************************************************************************
 * @file glcd.c
 * @author
 * @brief Driver for the ks108 GLCD screen
 *
 ***************************************************************************************************
 */

/* Includes --------------------------------------------------------------------------------------*/
#include "glcd.h"
#include <xc.h>
#include "main.h"

/* Private typedef -------------------------------------------------------------------------------*/

/* Private define --------------------------------------------------------------------------------*/
// #define _XTAL_FREQ 8000000 /**< OScillator frequency. Could be defined in main.h */

/* Private macro ---------------------------------------------------------------------------------*/

/* Private variables -----------------------------------------------------------------------------*/
/* 3x6 Font packed two per definition */
static const uint8_t Font3x6[65][3] = {
    0x00, 0x00, 0x00, /* Espace	0x20 */
    0x00, 0x5C, 0x00, /* ! */
    0x0C, 0x00, 0x0C, /* " */
    0x7C, 0x28, 0x7C, /* # */
    0x7C, 0x44, 0x7C, /* 0x */
    0x24, 0x10, 0x48, /* % */
    0x28, 0x54, 0x08, /* & */
    0x00, 0x0C, 0x00, /* ' */
    0x38, 0x44, 0x00, /* ( */
    0x44, 0x38, 0x00, /* ) */
    0x20, 0x10, 0x08, /* // */
    0x10, 0x38, 0x10, /* + */
    0x80, 0x40, 0x00, /* , */
    0x10, 0x10, 0x10, /* - */
    0x00, 0x40, 0x00, /* . */
    0x20, 0x10, 0x08, /* / */
    0x38, 0x44, 0x38, /* 0	0x30 */
    0x00, 0x7C, 0x00, /* 1 */
    0x64, 0x54, 0x48, /* 2 */
    0x44, 0x54, 0x28, /* 3 */
    0x1C, 0x10, 0x7C, /* 4 */
    0x4C, 0x54, 0x24, /* 5 */
    0x38, 0x54, 0x20, /* 6 */
    0x04, 0x74, 0x0C, /* 7 */
    0x28, 0x54, 0x28, /* 8 */
    0x08, 0x54, 0x38, /* 9 */
    0x00, 0x50, 0x00, /* : */
    0x80, 0x50, 0x00, /* ; */
    0x10, 0x28, 0x44, /* < */
    0x28, 0x28, 0x28, /* = */
    0x44, 0x28, 0x10, /* > */
    0x04, 0x54, 0x08, /* ? */
    0x38, 0x4C, 0x5C, /* @	0x40 */
    0x78, 0x14, 0x78, /* A */
    0x7C, 0x54, 0x28, /* B */
    0x38, 0x44, 0x44, /* C */
    0x7C, 0x44, 0x38, /* D */
    0x7C, 0x54, 0x44, /* E */
    0x7C, 0x14, 0x04, /* F */
    0x38, 0x44, 0x34, /* G */
    0x7C, 0x10, 0x7C, /* H */
    0x00, 0x7C, 0x00, /* I */
    0x20, 0x40, 0x3C, /* J */
    0x7C, 0x10, 0x6C, /* K */
    0x7C, 0x40, 0x40, /* L */
    0x7C, 0x08, 0x7C, /* M */
    0x7C, 0x04, 0x7C, /* N */
    0x7C, 0x44, 0x7C, /* O */
    0x7C, 0x14, 0x08, /* P	0x50 */
    0x38, 0x44, 0x78, /* Q */
    0x7C, 0x14, 0x68, /* R */
    0x48, 0x54, 0x24, /* S */
    0x04, 0x7C, 0x04, /* T */
    0x7C, 0x40, 0x7C, /* U */
    0x3C, 0x40, 0x3C, /* V */
    0x7C, 0x20, 0x7C, /* W */
    0x6C, 0x10, 0x6C, /* X */
    0x1C, 0x60, 0x1C, /* Y */
    0x64, 0x54, 0x4C, /* Z */
    0x7C, 0x44, 0x00, /* [ */
    0x08, 0x10, 0x20, /* \ */
    0x44, 0x7C, 0x00, /* ] */
    0x08, 0x04, 0x08, /* ^ */
    0x80, 0x80, 0x80, /* _ */
    0x04, 0x08, 0x00  /* `	0x60 */
};

/* 8x8 Font packed two per definition */
static const uint8_t Font8x8[2048] =
    {
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		0
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		1
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		2
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		3
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		4
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		5
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		6
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		7
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		8
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		9
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		10
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		11
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		12
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		13
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		14
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		15
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		16
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		17
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		18
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		19
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		20
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		21
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		22
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		23
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		24
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		25
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		26
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		27
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		28
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		29
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		30
        0, 0, 0, 0, 0, 0, 0, 0,                 //' '		31
        0, 0, 0, 0, 0, 0, 0, 0,                 //'SP'		32
        0, 6, 95, 95, 6, 0, 0, 0,               //'!'	33
        0, 7, 7, 0, 7, 7, 0, 0,                 //'"'	34
        20, 127, 127, 20, 127, 127, 20, 0,      //'#'	35
        36, 46, 107, 107, 58, 18, 0, 0,         //'$'	36
        70, 102, 48, 24, 12, 102, 98, 0,        //'%'	37
        48, 122, 79, 93, 55, 122, 72, 0,        //'&'	38
        4, 7, 3, 0, 0, 0, 0, 0,                 //'''	39
        0, 28, 62, 99, 65, 0, 0, 0,             //'('	40
        0, 65, 99, 62, 28, 0, 0, 0,             //')'	41
        8, 42, 62, 28, 28, 62, 42, 8,           //'*'	42
        8, 8, 62, 62, 8, 8, 0, 0,               //'+'	43
        0, 128, 224, 96, 0, 0, 0, 0,            //','	44
        8, 8, 8, 8, 8, 8, 0, 0,                 //'-'	45
        0, 0, 96, 96, 0, 0, 0, 0,               //'.'	46
        96, 48, 24, 12, 6, 3, 1, 0,             //'/'	47
        62, 127, 113, 89, 77, 127, 62, 0,       //'0'	48
        64, 66, 127, 127, 64, 64, 0, 0,         //'1'	49
        98, 115, 89, 73, 111, 102, 0, 0,        //'2'	50
        34, 99, 73, 73, 127, 54, 0, 0,          //'3'	51
        24, 28, 22, 83, 127, 127, 80, 0,        //'4'	52
        39, 103, 69, 69, 125, 57, 0, 0,         //'5'	53
        60, 126, 75, 73, 121, 48, 0, 0,         //'6'	54
        3, 3, 113, 121, 15, 7, 0, 0,            //'7'	55
        54, 127, 73, 73, 127, 54, 0, 0,         //'8'	56
        6, 79, 73, 105, 63, 30, 0, 0,           //'9'	57
        0, 0, 102, 102, 0, 0, 0, 0,             //':'	58
        0, 128, 230, 102, 0, 0, 0, 0,           //';'	59
        8, 28, 54, 99, 65, 0, 0, 0,             //'<'	60
        36, 36, 36, 36, 36, 36, 0, 0,           //'='	61
        0, 65, 99, 54, 28, 8, 0, 0,             //'>'	62
        2, 3, 81, 89, 15, 6, 0, 0,              //'?'	63
        62, 127, 65, 93, 93, 31, 30, 0,         //'@'	64
        124, 126, 19, 19, 126, 124, 0, 0,       //'A'	65
        65, 127, 127, 73, 73, 127, 54, 0,       //'B'	66
        28, 62, 99, 65, 65, 99, 34, 0,          //'C'
        65, 127, 127, 65, 99, 62, 28, 0,        //'D'
        65, 127, 127, 73, 93, 65, 99, 0,        //'E'
        65, 127, 127, 73, 29, 1, 3, 0,          //'F'
        28, 62, 99, 65, 81, 115, 114, 0,        //'G'
        127, 127, 8, 8, 127, 127, 0, 0,         //'H'
        0, 65, 127, 127, 65, 0, 0, 0,           //'I'
        48, 112, 64, 65, 127, 63, 1, 0,         //'J'
        65, 127, 127, 8, 28, 119, 99, 0,        //'K'
        65, 127, 127, 65, 64, 96, 112, 0,       //'L'
        127, 127, 14, 28, 14, 127, 127, 0,      //'M'
        127, 127, 6, 12, 24, 127, 127, 0,       //'N'
        28, 62, 99, 65, 99, 62, 28, 0,          //'O'
        65, 127, 127, 73, 9, 15, 6, 0,          //'P'
        30, 63, 33, 113, 127, 94, 0, 0,         //'Q'
        65, 127, 127, 9, 25, 127, 102, 0,       //'R'
        38, 111, 77, 89, 115, 50, 0, 0,         //'S'
        3, 65, 127, 127, 65, 3, 0, 0,           //'T'
        127, 127, 64, 64, 127, 127, 0, 0,       //'U'
        31, 63, 96, 96, 63, 31, 0, 0,           //'V'
        127, 127, 48, 24, 48, 127, 127, 0,      //'W'
        67, 103, 60, 24, 60, 103, 67, 0,        //'X'
        7, 79, 120, 120, 79, 7, 0, 0,           //'Y'
        71, 99, 113, 89, 77, 103, 115, 0,       //'Z'
        0, 127, 127, 65, 65, 0, 0, 0,           //'['
        1, 3, 6, 12, 24, 48, 96, 0,             //'\'
        0, 65, 65, 127, 127, 0, 0, 0,           //']'
        8, 12, 6, 3, 6, 12, 8, 0,               //'^'
        128, 128, 128, 128, 128, 128, 128, 128, //'_'
        0, 0, 3, 7, 4, 0, 0, 0,                 //'`'
        32, 116, 84, 84, 60, 120, 64, 0,        //'a'
        65, 127, 63, 72, 72, 120, 48, 0,        //'b'
        56, 124, 68, 68, 108, 40, 0, 0,         //'c'
        48, 120, 72, 73, 63, 127, 64, 0,        //'d'
        56, 124, 84, 84, 92, 24, 0, 0,          //'e'
        72, 126, 127, 73, 3, 2, 0, 0,           //'f'
        152, 188, 164, 164, 248, 124, 4, 0,     //'g'
        65, 127, 127, 8, 4, 124, 120, 0,        //'h'
        0, 68, 125, 125, 64, 0, 0, 0,           //'i'
        96, 224, 128, 128, 253, 125, 0, 0,      //'j'
        65, 127, 127, 16, 56, 108, 68, 0,       //'k'
        0, 65, 127, 127, 64, 0, 0, 0,           //'l'
        124, 124, 24, 56, 28, 124, 120, 0,      //'m'
        124, 124, 4, 4, 124, 120, 0, 0,         //'n'
        56, 124, 68, 68, 124, 56, 0, 0,         //'o'
        132, 252, 248, 164, 36, 60, 24, 0,      //'p'
        24, 60, 36, 164, 248, 252, 132, 0,      //'q'
        68, 124, 120, 76, 4, 28, 24, 0,         //'r'
        72, 92, 84, 84, 116, 36, 0, 0,          //'s'
        0, 4, 62, 127, 68, 36, 0, 0,            //'t'
        60, 124, 64, 64, 60, 124, 64, 0,        //'u'
        28, 60, 96, 96, 60, 28, 0, 0,           //'v'
        60, 124, 112, 56, 112, 124, 60, 0,      //'w'
        68, 108, 56, 16, 56, 108, 68, 0,        //'x'
        156, 188, 160, 160, 252, 124, 0, 0,     //'y'
        76, 100, 116, 92, 76, 100, 0, 0,        //'z'
        8, 8, 62, 119, 65, 65, 0, 0,            //'{'
        0, 0, 0, 119, 119, 0, 0, 0,             //'|'
        65, 65, 119, 62, 8, 8, 0, 0,            //'}
        2, 3, 1, 3, 2, 3, 1, 0,                 //'~'
        112, 120, 76, 70, 76, 120, 112, 0,      //''
        14, 159, 145, 177, 251, 74, 0, 0,       //'�' cyrilic A
        58, 122, 64, 64, 122, 122, 64, 0,       //'n'
        56, 124, 84, 85, 93, 25, 0, 0,          //'_'
        2, 35, 117, 85, 85, 125, 123, 66,       //'_'
        33, 117, 84, 84, 125, 121, 64, 0,       //'_'
        33, 117, 85, 84, 124, 120, 64, 0,       //'_'
        32, 116, 87, 87, 124, 120, 64, 0,       //'_'
        24, 60, 164, 164, 228, 64, 0, 0,        //'_'
        2, 59, 125, 85, 85, 93, 27, 2,          //'_'
        57, 125, 84, 84, 93, 25, 0, 0,          //'_'
        57, 125, 85, 84, 92, 24, 0, 0,          //'_'
        1, 69, 124, 124, 65, 1, 0, 0,           //'_'
        2, 3, 69, 125, 125, 67, 2, 0,           //'_'
        1, 69, 125, 124, 64, 0, 0, 0,           //'_'
        121, 125, 22, 18, 22, 125, 121, 0,      //'-'
        112, 120, 43, 43, 120, 112, 0, 0,       //'+'
        68, 124, 124, 85, 85, 69, 0, 0,         //'+'
        32, 116, 84, 84, 124, 124, 84, 84,      //'�'
        124, 126, 11, 9, 127, 127, 73, 0,       //'�'
        50, 123, 73, 73, 123, 50, 0, 0,         //'_'
        50, 122, 72, 72, 122, 50, 0, 0,         //'�'
        50, 122, 74, 72, 120, 48, 0, 0,         //'_'
        58, 123, 65, 65, 123, 122, 64, 0,       //'_'
        58, 122, 66, 64, 120, 120, 64, 0,       //'?'
        154, 186, 160, 160, 250, 122, 0, 0,     //'_'
        1, 25, 60, 102, 102, 60, 25, 1,         //'+'
        61, 125, 64, 64, 125, 61, 0, 0,         //'_'
        24, 60, 36, 231, 231, 36, 36, 0,        //'�'
        104, 126, 127, 73, 67, 102, 32, 0,      //'�'
        43, 47, 252, 252, 47, 43, 0, 0,         //'�'
        255, 255, 9, 9, 47, 246, 248, 160,      //'P'
        64, 192, 136, 254, 127, 9, 3, 2,        //'�'
        32, 116, 84, 85, 125, 121, 64, 0,       //' '
        0, 68, 125, 125, 65, 0, 0, 0,           //'_'
        48, 120, 72, 74, 122, 50, 0, 0,         //'_'
        56, 120, 64, 66, 122, 122, 64, 0,       //'�'
        122, 122, 10, 10, 122, 112, 0, 0,       //'�'
        125, 125, 25, 49, 125, 125, 0, 0,       //'-'
        0, 38, 47, 41, 47, 47, 40, 0,           //'�'
        0, 38, 47, 41, 47, 38, 0, 0,            //'�'
        48, 120, 77, 69, 96, 32, 0, 0,          //'+'
        56, 56, 8, 8, 8, 8, 0, 0,               //'_'
        8, 8, 8, 8, 56, 56, 0, 0,               //'�'
        79, 111, 48, 24, 204, 238, 187, 145,    //'+'
        79, 111, 48, 24, 108, 118, 251, 249,    //'+'
        0, 0, 0, 123, 123, 0, 0, 0,             //'�'
        8, 28, 54, 34, 8, 28, 54, 34,           //'�'
        34, 54, 28, 8, 34, 54, 28, 8,           //'+'
        170, 0, 85, 0, 170, 0, 85, 0,           //'_'
        170, 85, 170, 85, 170, 85, 170, 85,     //'_'
        221, 255, 170, 119, 221, 170, 255, 119, //'_'
        0, 0, 0, 255, 255, 0, 0, 0,             //'�'
        16, 16, 16, 255, 255, 0, 0, 0,          //'�'
        20, 20, 20, 255, 255, 0, 0, 0,          //'�'
        16, 16, 255, 255, 0, 255, 255, 0,       //'�'
        16, 16, 240, 240, 16, 240, 240, 0,      //'+'
        20, 20, 20, 252, 252, 0, 0, 0,          //'+'
        20, 20, 247, 247, 0, 255, 255, 0,       //'�'
        0, 0, 255, 255, 0, 255, 255, 0,         //'�'
        20, 20, 244, 244, 4, 252, 252, 0,       //'+'
        20, 20, 23, 23, 16, 31, 31, 0,          //'+'
        16, 16, 31, 31, 16, 31, 31, 0,          //'+'
        20, 20, 20, 31, 31, 0, 0, 0,            //'+'
        16, 16, 16, 240, 240, 0, 0, 0,          //'+'
        0, 0, 0, 31, 31, 16, 16, 16,            //'+'
        16, 16, 16, 31, 31, 16, 16, 16,         //'-'
        16, 16, 16, 240, 240, 16, 16, 16,       //'-'
        0, 0, 0, 255, 255, 16, 16, 16,          //'+'
        16, 16, 16, 16, 16, 16, 16, 16,         //'-'
        16, 16, 16, 255, 255, 16, 16, 16,       //'+'
        0, 0, 0, 255, 255, 20, 20, 20,          //'�'
        0, 0, 255, 255, 0, 255, 255, 16,        //'�'
        0, 0, 31, 31, 16, 23, 23, 20,           //'+'
        0, 0, 252, 252, 4, 244, 244, 20,        //'+'
        20, 20, 23, 23, 16, 23, 23, 20,         //'-'
        20, 20, 244, 244, 4, 244, 244, 20,      //'-'
        0, 0, 255, 255, 0, 247, 247, 20,        //'�'
        20, 20, 20, 20, 20, 20, 20, 20,         //'-'
        20, 20, 247, 247, 0, 247, 247, 20,      //'+'
        20, 20, 20, 23, 23, 20, 20, 20,         //'-'
        16, 16, 31, 31, 16, 31, 31, 16,         //'-'
        20, 20, 20, 244, 244, 20, 20, 20,       //'-'
        16, 16, 240, 240, 16, 240, 240, 16,     //'-'
        0, 0, 31, 31, 16, 31, 31, 16,           //'+'
        0, 0, 0, 31, 31, 20, 20, 20,            //'+'
        0, 0, 0, 252, 252, 20, 20, 20,          //'+'
        0, 0, 240, 240, 16, 240, 240, 16,       //'+'
        16, 16, 255, 255, 16, 255, 255, 16,     //'+'
        20, 20, 20, 255, 255, 20, 20, 20,       //'+'
        16, 16, 16, 31, 31, 0, 0, 0,            //'+'
        0, 0, 0, 240, 240, 16, 16, 16,          //'+'
        255, 255, 255, 255, 255, 255, 255, 255, //'_'
        240, 240, 240, 240, 240, 240, 240, 240, //'_'
        255, 255, 255, 255, 0, 0, 0, 0,         //'�'
        0, 0, 0, 0, 255, 255, 255, 255,         //'_'
        15, 15, 15, 15, 15, 15, 15, 15,         //'_'
        56, 124, 68, 108, 56, 108, 68, 0,       //'_'
        252, 254, 42, 42, 62, 20, 0, 0,         //'_'
        126, 126, 2, 2, 6, 6, 0, 0,             //'_'
        2, 126, 126, 2, 126, 126, 2, 0,         //'�'
        99, 119, 93, 73, 99, 99, 0, 0,          //'_'
        56, 124, 68, 124, 60, 4, 4, 0,          //'_'
        128, 254, 126, 32, 32, 62, 30, 0,       //'�'
        4, 6, 2, 126, 124, 6, 2, 0,             //'_'
        153, 189, 231, 231, 189, 153, 0, 0,     //'_'
        28, 62, 107, 73, 107, 62, 28, 0,        //'_'
        76, 126, 115, 1, 115, 126, 76, 0,       //'_'
        48, 120, 74, 79, 125, 57, 0, 0,         //'_'
        24, 60, 36, 60, 60, 36, 60, 24,         //'_'
        152, 252, 100, 60, 62, 39, 61, 24,      //'_'
};

/* Variables positionnement */
/* x et y serviront à la sauvegarde des coordonnées absolues de l'écran */
static uint8_t x = 0;
static uint8_t y = 0;

/* Private function prototypes -------------------------------------------------------------------*/
static void wait_for_release(void);

/* Private functions -----------------------------------------------------------------------------*/

static void wait_for_release(void)
{
    while (PORTEbits.RE0)
    {
        // Do nothing
    }
}

void glcd_Init(glcd_mode_t mode)
{
    ADCON1 |= 0b00001111;

    TRISB &= ~0b00111111;
    PORTB &= ~0b00111111;

    TRISD = 0x00;
    PORTD = 0x00;

    // Reset the display
    GLCD_RST = 0;
    __delay_us(10);
    GLCD_RST = 1;

    GLCD_E = 0;
    GLCD_CS1 = 0;
    GLCD_CS2 = 0;
    GLCD_RS = 0;
    // d�lai pour initialisation
    __delay_ms(10);
    glcd_WriteByte(GLCD_LEFT, 0xC0);  // Specifie la premi�re ligne RAM line en haut
    glcd_WriteByte(GLCD_RIGHT, 0xC0); //   de l'�cran
    glcd_WriteByte(GLCD_LEFT, 0x40);  // Place l'adresse de colonne � 0
    glcd_WriteByte(GLCD_RIGHT, 0x40);
    glcd_WriteByte(GLCD_LEFT, 0xB8); // Place l'adresse de la page � 0
    glcd_WriteByte(GLCD_RIGHT, 0xB8);

    if (mode == GLCD_ON)
    {
        TRISA = 0x00;
        PORTA = 0xFF;
        glcd_WriteByte(GLCD_LEFT, 0x3F); // Allume le GLCD
        glcd_WriteByte(GLCD_RIGHT, 0x3F);
    }
    else
    {
        glcd_WriteByte(GLCD_LEFT, 0x3E); // Eteint le GLCD
        glcd_WriteByte(GLCD_RIGHT, 0x3E);
    }

    glcd_FillScreen(0); // CLearScreen !
}

void glcd_WriteByte(glcd_side_t side, uint8_t data)
{
    if (side == GLCD_RIGHT)
    { // S�lection du cot� pour l'�criture
        GLCD_CS1 = 1;
        GLCD_CS2 = 0;
    }
    else
    {
        GLCD_CS2 = 0;
        GLCD_CS2 = 1;
    }

    GLCD_DATA_TRIS = 0; // Port D en sortie
    GLCD_RW = 0;        // Positionnement du bit pour �criture

    WR_DATA = data; // Placement des donn�es sur le registre du GLCD

    GLCD_E = 1; // Passage de E de 0 � 1
    __delay_us(1);
    GLCD_E = 0; // Passage de E de 1 � 0
    __delay_us(1);
    // Le GLCD r�cup�re les donn�es !

    GLCD_CS1 = 0;
    GLCD_CS2 = 0; // relachement des ChipSelect
}

uint8_t glcd_ReadByte(glcd_side_t side)
{
    uint8_t data;

    if (side == GLCD_RIGHT)
    { // S�lection du cot� pour l'�criture
        GLCD_CS1 = 1;
        GLCD_CS2 = 0;
    }
    else
    {
        GLCD_CS2 = 0;
        GLCD_CS2 = 1;
    }

    GLCD_DATA_TRIS = 0xFF; // Port D en entr�e
    GLCD_RW = 1;           // Positionnement du bit pour lecture

    GLCD_E = 1; // Passage de E de 0 � 1
    __delay_us(1);

    data = RD_DATA; // R�cup�ration des donn�es
    GLCD_E = 0;     // Passage de E de 1 � 0
    __delay_us(1);
    GLCD_CS1 = 0;
    GLCD_CS2 = 0; // relachement des ChipSelect

    return data;
}

void glcd_PlotPixel(uint8_t xpos, uint8_t ypos, glcd_color_t color)
{
    uint8_t data;
    glcd_side_t side = GLCD_LEFT; // On initialise sur le cot� gauche

    if (xpos > 63) // Si ce n'est pas le c�t� gauche, c'est le droit
    {
        xpos -= 64;
        side = GLCD_RIGHT;
    }
    GLCD_RS = 0; // Positionnement du bit pour instruction (adressage)

    xpos &= 0b01111111;                                 // force � 0 le MSB
    xpos |= 0b01000000;                                 // Positionne � 1 le bit 6.
    glcd_WriteByte(side, (xpos));                       // Envoi la position horizontale
    glcd_WriteByte(side, (((ypos / 8)) & 0xBF) | 0xB8); // Envoi la position verticale (page)

    GLCD_RS = 1; // Positionnement du bit pour r�cup�ration de donn�es

    glcd_ReadByte(side);        // On doit lire 2 fois pour obtenir les donn�es
    data = glcd_ReadByte(side); //  � l'adresse intialis�e

    GLCD_RS = 0; // Positionnement du bit pour instruction (adressage)

    glcd_WriteByte(side, xpos); // reinitialise la position horizontale, incrementer lors de la lecture

    if (color == GLCD_WHITE)
    {
        data = (data) | (uint8_t)(1 << (ypos % 8)); // Allume le pixel sans modifier les autres
    }

    else
    {
        data = (data) & (~(1 << (ypos % 8))); // Eteint le pixel sans modifier les autres
    }

    GLCD_RS = 1; // Positionnement du bit pour envoi de donn�es

    glcd_WriteByte(side, data); // On �crit les donn�es
}

void glcd_Rect(uint8_t xs, uint8_t ys, uint8_t xe, uint8_t ye, glcd_color_t color)
{
    if (ys > ye)
    {
        return;
    }

    if (xs > xe)
    {
        return;
    }

    for (uint8_t i = xs; i <= xe; i++)
    {
        for (uint8_t j = ys; j <= ye; j++)
        {
            if (i == xs || i == xe || j == ye || j == ys)
            {
                glcd_PlotPixel(i, j, color);
            }
        }
    }
}

void glcd_FillScreen(glcd_color_t color)
{

    for (uint8_t i = 0; i < 8; i++) // Boucle sur les pages verticales
    {
        GLCD_RS = 0;                           // Positionnement du bit pour instruction (adressage)
        glcd_WriteByte(GLCD_LEFT, 0b01000000); // Envoi la position horizontale � 0
        glcd_WriteByte(GLCD_RIGHT, 0b01000000);
        glcd_WriteByte(GLCD_LEFT, i | 0b10111000); // Envoi la position verticale (page 0)
        glcd_WriteByte(GLCD_RIGHT, i | 0b10111000);
        GLCD_RS = 1; // Positionnement du bit pour transfert de donn�es

        for (uint8_t j = 0; j < 64; j++) // Boucle sur les colonnes
        {
            glcd_WriteByte(GLCD_LEFT, 0xFF * color); // Allume ou �teint les pixels
            glcd_WriteByte(GLCD_RIGHT, 0xFF * color);
        }
    }
}

void glcd_SetCursor(uint8_t xpos, uint8_t ypos)
{
    glcd_side_t side = GLCD_LEFT; // On initialise sur le cot� gauche

    if (xpos > 127 | ypos > 7)
    { // Si les coordonn�es sont Hors limite, on ne traite pas
        return;
    }

    x = xpos; // Sauvegarde des donn�es position absolue
    y = ypos;

    if (xpos > 63) // Si ce n'est pas le c�t� gauche, c'est le droit
    {
        xpos -= 64; // xpos est la position relative au controleur G ou D
        side = GLCD_RIGHT;
    }

    GLCD_RS = 0;                       // Placement du bit pour envoi instruction (adressage)
    glcd_WriteByte(side, 0x40 | xpos); // Envoi de l'adresse horizontale
    glcd_WriteByte(side, 0xB8 | ypos); // Envoi de l'adresse verticale
    GLCD_RS = 1;                       // Placement du bit pour transfert de donn�e
}

void glcd_WriteChar8X8(unsigned char ch, glcd_color_t color)
{
    uint8_t xpos = 0;
    glcd_side_t side = GLCD_LEFT; // On initialise sur le cot� gauche
    uint16_t chr = 0;

    if (ch == '\n') // d�tection CR
    {
        x = 0;
        y++;
        return;
    }

    if (x > 63) // Si ce n'est pas le c�t� gauche, c'est le droit
    {
        side = GLCD_RIGHT;
        xpos = x - 64; // x d�signe la position absolue,
    }                  // xpos est la position / au controleur doit ou gauche
    else
    {
        xpos = x; // Lorsque l'on est � gauche x=xpos
    }

    chr = (uint16_t)ch * 8; // Positionnement de chr au d�but du caract�re (8 bytes par caract�re)

    for (uint8_t i = 0; i < 8; i++) // on balaye les 8 colonnes du caract�re
    {
        // if((xpos+i) > 63)             	// Si le caract�re se trouve entre les deux moiti�s, on traite !
        if (xpos > 63)
        {
            xpos -= 64;
            side = GLCD_RIGHT;
            GLCD_RS = 0;                       // Positionnement du bit pour instruction (adressage)
            glcd_WriteByte(side, 0x40 | xpos); // on repositionne le curseur du GLCD
            glcd_WriteByte(side, 0xB8 | y);    // sur le c�t� droit
            GLCD_RS = 1;                       // Positionnement du bit pour transfert de donn�es
        }
        if (color == GLCD_WHITE)
        {
            glcd_WriteByte(side, Font8x8[chr + i]); // on �crit le caract�re
        }

        else
        {
            glcd_WriteByte(side, ~(Font8x8[chr + i]));
        }

        xpos++;
    }
    x += 8;
}

void glcd_WriteChar3x6(unsigned char ch, glcd_color_t color)
{
    uint8_t xpos = 0;
    glcd_side_t side = GLCD_LEFT; // On initialise sur le cot� gauche

    if (ch == '\n') // d�tection CR
    {
        x = 0;
        y++;
        return;
    }

    if (x > 63) // Si ce n'est pas le c�t� gauche, c'est le droit
    {
        side = GLCD_RIGHT;
        xpos = x - 64; // x d�signe la position absolue,
    }                  // xpos est la position / au controleur doit ou gauche
    else
    {
        xpos = x; // Lorsque l'on est � gauche x=xpos
    }

    ch -= 32;

    for (uint8_t i = 0; i < 3; i++) // on balaye les 8 colonnes du caract�re
    {
        if (xpos > 63)
        {
            xpos -= 64;
            side = GLCD_RIGHT;
            GLCD_RS = 0;                       // Positionnement du bit pour instruction (adressage)
            glcd_WriteByte(side, 0x40 | xpos); // on repositionne le curseur du GLCD
            glcd_WriteByte(side, 0xB8 | y);    // sur le c�t� droit
            GLCD_RS = 1;                       // Positionnement du bit pour transfert de donn�es
        }
        if (color == GLCD_WHITE)
        {
            glcd_WriteByte(side, Font3x6[ch][i]); // on �crit le caract�re
        }

        else
        {
            glcd_WriteByte(side, ~(Font3x6[ch][i]));
        }

        xpos++;
    }
    x += 5;
}

void glcd_WriteString(const char str[], uint8_t len, glcd_font_t font, glcd_color_t color)
{
    for (uint8_t i = 0; i < len; i++)
    {
        /* End of string detected */
        if (str[i] == '\0')
        {
            return;
        }

        if (font == F8X8)
        {
            glcd_WriteChar8X8(str[i], color);
        }
        else
        {
            glcd_WriteChar3x6(str[i], color);
        }
    }
}

void glcd_text_write(const char str[], uint8_t len, uint8_t x, uint8_t y)
{
    /* Place cursor and write the string */
    glcd_SetCursor(x, y);
    glcd_WriteString(str, len, F8X8, 1);
}
