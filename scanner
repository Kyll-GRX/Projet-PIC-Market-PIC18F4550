// PIC18F UART => USART   on pin RC6 for Tx and RC7 for Rx 
// Scanner works in 8N1 UART configuration (8bits DATA + NOJE bit PARITY + 1bit STOP) 
// PIC receives, analyses and verifies the data by itself, and puts the results (8bits DATA) in the register RCREG 
// we must read this register and put/add (like append) its value in a buffer (complete_data[])
// (the unique value is one of the several data frames sent, one by one, by scanner representing then the entire barcode Value)  
// and repeat this until we found value 0x0D in the RCREG (means chariot so end of transmission by the scanner module) 

// --- CONFIGURATION BITS (Fosc = 16MHz via HSPLL et CPUDIV, Watchdog OFF) ---
#pragma config PLLDIV  = 4          // 16MHz / 4 = 4MHz vers la PLL USB (sans effet sur le CPU ici)
#pragma config CPUDIV  = OSC1_PLL2  // CPU = Fosc / 1
#pragma config USBDIV  = 1
#pragma config FOSC    = HS         // Quartz HS 8MHz -> Fosc = 8MHz
#pragma config WDT     = OFF        // Watchdog OFF (sinon reset permanent)
#pragma config PBADEN  = OFF        // PORTB en numerique
#pragma config LVP     = OFF        // Low Voltage Programming OFF
#pragma config MCLRE   = ON


#include <xc.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <stdint.h> 


    #define LED_GREEN        LATEbits.LATE0 
    #define LED_RED          LATEbits.LATE1   
    #define BUZZER           LATCbits.LATC2              // Broche physique du buzzer (CCP1) 

    #define XTAL_FREQ        16000000UL                  // Fosc CPU ajusté à 16 MHz pour le PWM
    #define TICKS_PER_MS     (XTAL_FREQ / 4 / 1000UL)    // 4000 ticks per ms
    static volatile uint32_t ms_count = 0;


// Configuration of the buzzer, RC2 as an output (as RC2 is the official PWM pin of PIC18F)
// DutyCyle for PWM value to send to Buzzer in order to play a frequency tone is defined by :
// Freq_PWM = Fosc / (4* Prescale* (PR+))  with Prescale=16   where DutyCycle is 50% of the PR so (PR+1)/2
// so for 2.5kHz correct --> DutyCyle = { [(16*10^6) / (4*16*2500) -1 =99] +1} /2 = 50 !
    #define DUTYCYCLE_CORRECT     50           // for 2.5 kHz
    #define DUTYCYCLE_WRONG       83           // for 1.5 kHz

    #define BUFFER_SIZE 32
    volatile char rx_buffer[BUFFER_SIZE];
    volatile unsigned char rx_index = 0;
    volatile unsigned char barcode_ready = 0; 
    unsigned char barcode_length = 0;

    
    
void init(void) { 
    // Configuration des broches RX (RC7) et TX (RC6) en entrées/sorties numériques
        TRISCbits.TRISC6 = 1;  // TX
        TRISCbits.TRISC7 = 1;  // RX
        TXSTAbits.SYNC = 0;    // Mode asynchrone
        TXSTAbits.TXEN = 1;    // Active la transmission

    // Configuration of register TXSTA (Transmission)
        TXSTAbits.SYNC = 0;    // Asynchrone mode
        TXSTAbits.TXEN = 1;    // Enable transmission

    // Configuration of register RCSTA (Réception) 
        RCSTAbits.SPEN = 1;    // Enable Serial Port
        RCSTAbits.CREN = 1;    // Enable Continuous Reception
    
    // Configuration of the Output LEDs for items scan validation
        ADCON1 = 0x0F;         // Almost all ports as Digital 
        TRISEbits.TRISE0 = 0;  // Set D0 as output (Green LED) (output=0 | input=1) 
        TRISEbits.TRISE1 = 0;  // Set D1 as output (Green LED) (output=0 | input=1) 
        LED_GREEN = 0;         // RC4 GREEN
        LED_RED = 0;           // RC5 RED
        
    //Configuration of the Buzzer 
        TRISCbits.TRISC2 = 0;  // RC2 as output linked to buzzer
        LATCbits.LATC2 = 0;    // as RC2 is one of the PWM pins of the PIC18F


    // HOW BAUDRATE SELECTION WORKS ? 
        // Baudrate = Fosc / (4 * (SPBRG+1))
        // that's the formule to set BaudRate, but we need to know which value of SPBRG leads to BdRate=9600
        // calculs... SPBRG = 416  so 9bits ! so we might use TWO SPBRG registers (each one of 1byte) 
        // (416)_10  ==  (1 1010 0000)_2   -->  SPBRGH (high) = 0000 00001   11  SPBRG (low) = 0011 1000 
        BAUDCONbits.BRG16 = 1;   // Enable SPBRG on 16bits if=1 (8bits if=0) 
        TXSTAbits.BRGH = 1;    // Enable the use of the second byte SPBRGH (High) 
        SPBRGH = 0b00000001;   // High byte of 416
        SPBRG = 0b10100000;    // Low byte of 416

    // Configuration of Interrupts
        PIE1bits.RCIE = 1;     // Enable Interrupts at the Reception (page 108/438 datasheet) 
        PIR1bits.RCIF = 0;     // Clears the Interrupts Flag (page 106/438 datasheet) 
        IPR1bits.RCIP = 0;     // UART en basse priorité (low_isr)
        INTCONbits.PEIE = 1;   // Peripheral Interrupts Enable (PIE) (page 103/438 datasheet)
        INTCONbits.GIE = 1;    // Global Interrupts Enable (GIE) (page 103/438 datasheet)
        RCONbits.IPEN = 1;     // Enable Interrupts Priority Gestion
}



void __interrupt(high_priority) high_isr(void) {
    // ISR Flag verification about UART communications
    if (PIR2bits.CCP2IF) {
        PIR2bits.CCP2IF = 0;
        ms_count++; // Incrémente le compteur milliseconde exactement toutes les 1 ms
    }
    
    // ISR Flag verification about USB communications
    // is flag USB ...  
}

void __interrupt(low_priority) low_isr(void) {
    // ISR Flag verification about UART communications
    if (PIR1bits.RCIF) {
        char received_char = RCREG;   // read data from RCREG register and clear RCIF interrupt flag
    
        if (received_char == 0x0D) {     // end of UART data transmission
            rx_buffer[rx_index++] = '\0' ;  // entire BarCode data received
            barcode_length = rx_index;   // 
            barcode_ready = 1;           // kind of soft flag to indicate to main_loop that a complete barcode is ready to be read
            rx_index = 0;                   // of course reset index for a new barcode 
        } 
        else {
            if (rx_index < (BUFFER_SIZE - 1)) {
                rx_buffer[rx_index++] = received_char;
            }
        }   
    }
    
    if (RCSTAbits.OERR) { RCSTAbits.CREN = 0; RCSTAbits.CREN = 1; }
    
    
    // ISR Flag verification about XXXX communications
    // if ...
}

void Start_Buzzer(uint8_t dutyCycle) {
    PR2 = 2*dutyCycle-1;       // Define period (frequency) 
    CCPR1L = dutyCycle;      // Define dutyCycle as half the period 
    CCP1CON = 0b00001100;    // Enable PWM mode on CCP1 
    T2CONbits.T2CKPS0 = 1;   // set Prescaler as 1:16 (p139/438 datasheet) 
    T2CONbits.T2CKPS1 = 1;   // set Prescaler as 1:16 (p139/438 datasheet) 
    T2CONbits.TMR2ON = 1;    // Enable Timer2 bit n°2
    // could also be written as : T2CON = 0b00000111; 
} 

void Stop_Buzzer() {
    CCP1CON = 0x00;   // Disable PWM mode on CCP1 
    T2CON = 0x00;     // Disable Timer2 (used by the CCP registers) 
    BUZZER = 0;       // Switch OFF the buzzer 
}



void timer1_init(void) {
    // Selon la datasheet p133, le TIMER1 est en 16bits (utile pour 1000ms > 256) 
    // et a un counter internet 16bits aussi, TMR1H & TMR1L
    
    T3CON = 0x00;                // CCP1/CCP2 utilisent Timer1 comme base de temps
    T1CONbits.RD16 = 1;          // Enable register read/write in one 16bits operation (p133/648 of datasheet))
    T1CONbits.TMR1CS = 0;        // Horloge interne (Fosc=48MHz / 4) -> 12 MHz
    T1CONbits.TMR1ON = 0;        // Activate the Timer
    // could also be written as :  T1CON = 0b10000000;  RD16=1, prescaler 1:1, T1OSCEN=0, TMR1CS=0 (Fcy), TMR1ON=0
    
    TMR1H   = 0;         
    TMR1L   = 0;
    CCPR2   = TICKS_PER_MS - 1;   // period = 4000 ticks per 1 ms at Fosc=16MHz 
    CCP2CON = 0b00001011;         // Compare, Special Event Trigger (reset TMR1)

    PIR2bits.CCP2IF = 0;
    IPR2bits.CCP2IP = 1;           // Timer/CCP2 in High Priority 
    PIE2bits.CCP2IE = 1;

    T1CONbits.TMR1ON = 1;          // START Timer1 !
}


uint32_t millis(void) {            // lecture atomique sans couper les IT
    uint32_t a, b;
    do { a = ms_count; b = ms_count; } while (a != b);
    return a;
}

void delay_ms(uint16_t n) { 
    uint32_t start = millis();
    while ((uint32_t)(millis() - start) <= n);   // n+1 ticks => délai dans [n, n+1] ms
}


// --- FEEDBACK VALIDE (TS2.5 & TS2.6) ---
void Feedback_ValidProduct(void) {
    LED_GREEN = 1;                      // Switch ON Green Led
    Start_Buzzer(DUTYCYCLE_CORRECT);    // Buzzer at 2.5kHz
    delay_ms(100);                      // 100ms (TS2.6) 
    Stop_Buzzer();                      // Switch OFF buzzer
    delay_ms(1900);                     // Continue to 2000ms (100ms + 1900ms) (TS2.5)  
    LED_GREEN = 0;                      // Switch OFF Green Led
}


// --- FEEDBACK INCONNU (TS2.7 & TS2.8) ---
void Feedback_UnknownProduct(void) {
    LED_RED = 1;                      // Switch ON Green Led
    Start_Buzzer(DUTYCYCLE_WRONG);    // Buzzer at 2.5kHz
    delay_ms(300);                    // 100ms (TS2.8) 
    Stop_Buzzer();                    // Switch OFF buzzer
    delay_ms(1700);                   // Continue to 2000ms (300ms + 1700ms) (TS2.7)  
    LED_RED = 0;                      // Switch OFF Green Led
}



void main(void) {
    init();
    timer1_init(); 
    
    LED_GREEN = 1; 
    PORTEbits.RE0 = 1;
    Feedback_ValidProduct();
    Feedback_UnknownProduct();
    Feedback_ValidProduct ();
    Feedback_UnknownProduct();
    
    while(1) {  
        if (barcode_ready) {
            // Traitement du code-barres reçu dans rx_buffer
            // Exemple de test factice :
            if (rx_buffer[0] == '1') {
                Feedback_ValidProduct();
            } else {
                Feedback_UnknownProduct();
            }
            barcode_ready = 0;
        }
    }
}
