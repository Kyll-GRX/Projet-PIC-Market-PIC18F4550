/**
 * @file    main.c
 * @brief   PIC-MARKET - Menus du GLCD (1re soutenance)
 * @details Etape 2 : reception des codes-barres par UART (interruption) -> recherche
 *          dans le catalogue -> affichage du nom et du prix sur le GLCD.
 *
 *          GLCD 128 x 64 : 16 caracteres x 8 lignes (police 8x8).
 *          glcd_text_write(texte, longueur max, x en pixels, ligne 0..7)
 *          Regle : x = 4, 12, 20, 28... pour qu'aucun caractere ne commence pile en x = 64
 *          (frontiere entre les 2 controleurs de l'ecran, cas mal gere par glcd.c).
 */

/* Bits de configuration (sans eux : oscillateur EC, LVP actif sur RB5, chien de garde actif) */
#pragma config FOSC   = HS      // Quartz 8 MHz
#pragma config PLLDIV = 2, CPUDIV = OSC1_PLL2, USBDIV = 2
#pragma config FCMEN  = OFF, IESO = OFF
#pragma config PWRT   = ON, BOR = ON, BORV = 3, VREGEN = OFF
#pragma config WDT    = OFF     // Chien de garde desactive
#pragma config WDTPS  = 32768
#pragma config CCP2MX = ON
#pragma config PBADEN = OFF     // RB0..RB4 numeriques (lignes de controle du GLCD)
#pragma config LPT1OSC = OFF
#pragma config MCLRE  = ON
#pragma config STVREN = ON
#pragma config LVP    = OFF     // Libere RB5 (reset du GLCD)
#pragma config ICPRT  = OFF
#pragma config XINST  = OFF
#pragma config CP0 = OFF, CP1 = OFF, CP2 = OFF, CP3 = OFF, CPB = OFF, CPD = OFF
#pragma config WRT0 = OFF, WRT1 = OFF, WRT2 = OFF, WRT3 = OFF, WRTC = OFF, WRTB = OFF, WRTD = OFF
#pragma config EBTR0 = OFF, EBTR1 = OFF, EBTR2 = OFF, EBTR3 = OFF, EBTRB = OFF

#include <string.h>
#include "main.h"
#include "glcd.h"
#include "uart.h"

/* =============================== Catalogue des produits =============================== */

typedef struct
{
    const char *code;   // code-barres (texte ASCII, sans le CR final)
    const char *nom;    // nom affiche sur le GLCD (15 caracteres max)
    uint16_t    prix;   // prix en CENTIMES (115 = 1,15 EUR)
} produit_t;

/* Catalogue - DONNEES DE TEST (produits et codes fictifs).
 * Codes commencant par 200 : plage GS1 20-29 reservee aux codes internes des magasins,
 * ils ne correspondent donc a aucun produit reel.
 * 'const' -> range en memoire Flash (32 Ko) et non en RAM (2 Ko). */
static const produit_t catalogue[] =
{
    { "2000000000015", "Lait 1L",          115 },
    { "2000000000022", "Cafe moulu 250g",  349 },
    { "2000000000039", "Pates 500g",        99 },
};

#define NB_PRODUITS  (sizeof(catalogue) / sizeof(catalogue[0]))

/* Cherche un code dans le catalogue.
 * Retourne l'index du produit (0, 1, 2...) ou -1 si le code est inconnu. */
int8_t chercher_produit(const char *code)
{
    for (uint8_t i = 0; i < NB_PRODUITS; i++)
    {
        if (strcmp(code, catalogue[i].code) == 0)   // 0 = les deux textes sont identiques
        {
            return (int8_t)i;
        }
    }
    return -1;                                      // tout le catalogue parcouru : inconnu
}

/* ==================================== Menus du GLCD ==================================== */

void menu_accueil(void)
{
    glcd_FillScreen(GLCD_BLUE);                    // efface l'ecran
    glcd_text_write("PIC MARKET", 10, 20, 1);
    glcd_text_write("Bienvenue !", 11, 20, 3);
    glcd_text_write("Scannez un", 10, 20, 5);
    glcd_text_write("produit", 7, 36, 6);
}

void menu_produit_reconnu(const char *nom, const char *prix)
{
    glcd_FillScreen(GLCD_BLUE);
    glcd_text_write(nom, 15, 4, 1);                // 15 car. max, s'arrete au '\0'
    glcd_text_write("Prix :", 6, 4, 3);
    glcd_text_write(prix, 15, 4, 5);
}

void menu_produit_inconnu(const char *code)
{
    glcd_FillScreen(GLCD_BLUE);
    glcd_text_write("PRODUIT INCONNU", 15, 4, 1);
    glcd_text_write(code, 15, 4, 3);
    glcd_text_write("Non ajoute", 10, 20, 5);
}

void menu_panier(const char *total)
{
    glcd_FillScreen(GLCD_BLUE);
    glcd_text_write("PIC MARKET", 10, 20, 1);
    glcd_text_write("TOTAL :", 7, 4, 3);
    glcd_text_write(total, 15, 4, 5);
}

void menu_transaction_annulee(void)
{
    glcd_FillScreen(GLCD_BLUE);
    glcd_text_write("TRANSACTION", 11, 20, 2);
    glcd_text_write("ANNULEE", 7, 36, 4);
}

/* Ecran affiche quand l'UART a rejete un code (voir les UART_ERR_* dans uart.h) */
void menu_erreur_lecture(void)
{
    glcd_FillScreen(GLCD_BLUE);
    glcd_text_write("ERREUR LECTURE", 14, 4, 2);
    glcd_text_write("Rescannez", 9, 28, 4);
}

/* Prix en centimes -> texte "3,49 EUR" (sans sprintf, trop lourd pour le PIC).
 * out : au moins 11 octets ("655,35 EUR" + '\0'). */
static void format_prix(uint16_t centimes, char *out)
{
    uint16_t euros = centimes / 100;
    uint8_t  cts   = (uint8_t)(centimes % 100);
    char     tmp[5];
    uint8_t  n = 0;
    uint8_t  k = 0;

    do                                       /* chiffres des euros, a l'envers */
    {
        tmp[n++] = (char)('0' + (euros % 10));
        euros /= 10;
    } while (euros > 0);

    while (n > 0)                            /* remis dans le bon ordre */
    {
        out[k++] = tmp[--n];
    }
    out[k++] = ',';
    out[k++] = (char)('0' + (cts / 10));
    out[k++] = (char)('0' + (cts % 10));
    out[k++] = ' ';
    out[k++] = 'E';
    out[k++] = 'U';
    out[k++] = 'R';
    out[k]   = '\0';
}

/* ==================================== Interruptions ==================================== */

/* Une seule ISR (priorites desactivees, IPEN = 0 par defaut).
 * Elle reste tres courte : elle range l'octet recu, le traitement se fait dans main(). */
void __interrupt() isr(void)
{
    if (PIE1bits.RCIE && PIR1bits.RCIF)
    {
        uart_isr();
    }
}

/* ======================================== main ========================================= */

void main(void)
{
    char code[BARCODE_MAX_LEN + 1];
    char prix_txt[12];

    glcd_Init(GLCD_ON);
    menu_accueil();

    uart_init();
    INTCONbits.PEIE = 1;                     /* interruptions des peripheriques (EUSART) */
    INTCONbits.GIE  = 1;                     /* autorisation generale                    */

    while (1)
    {
        if (uart_get_barcode(code))          /* un code complet (termine par CR) est arrive */
        {
            int8_t i = chercher_produit(code);

            if (i >= 0)
            {
                format_prix(catalogue[i].prix, prix_txt);
                menu_produit_reconnu(catalogue[i].nom, prix_txt);
            }
            else
            {
                menu_produit_inconnu(code);
            }
        }

        if (uart_get_and_clear_errors() != 0)
        {
            menu_erreur_lecture();
        }
    }
}
