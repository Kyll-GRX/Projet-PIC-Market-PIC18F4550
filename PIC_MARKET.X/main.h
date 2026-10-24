/**
 * @file    main.h
 * @brief   PIC-MARKET - Configuration globale et menus du GLCD
 * @details Inclus par main.c et glcd.c (glcd.c a besoin de _XTAL_FREQ pour __delay_us/ms).
 *          Les #pragma config sont dans main.c uniquement.
 */
#ifndef MAIN_H
#define MAIN_H

#define _XTAL_FREQ 8000000UL    /* Quartz 8 MHz de l'EasyPIC v7, mode HS sans PLL */

#include <xc.h>
#include <stdint.h>

/* Catalogue */
int8_t chercher_produit(const char *code);   /* index du produit ou -1 */

/* Menus du GLCD */
void menu_accueil(void);
void menu_produit_reconnu(const char *nom, const char *prix);
void menu_produit_inconnu(const char *code);
void menu_panier(const char *total);
void menu_transaction_annulee(void);
void menu_erreur_lecture(void);

#endif /* MAIN_H */
