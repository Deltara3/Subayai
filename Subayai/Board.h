/*
 * Board.h
 * Hardware-specific definitions that contain baud, pins, and helper functions.
 */

#pragma once

#include <Arduino.h>

// There's not a big reason for changing this but you can if you want.
#define BAUD_RATE 1000000

// Blinks LED if Sensor fails to get a config, only disable if you need pin 13.
#define LED_WARNING

// Update this to add, remove, or update set pins for each key.
#define KEY_LIST \
    X(C, PC2) \
    X(C, PC3)

#define X(port, bit) + 1
constexpr uint8_t NUM_KEYS = 0 KEY_LIST;
#undef X

// You probably shouldn't touch this.
constexpr uint8_t MAX_KEYS = 16;

#if defined(__AVR_ATmega328P__)
    struct Pin {
        volatile uint8_t* port;
        volatile uint8_t* ddr;
        volatile uint8_t* pin;
        uint8_t bit;
    };

    #define PIN(port, bit) Pin { &PORT##port, &DDR##port, &PIN##port, (1 << bit) }

    #if defined(LED_WARNING)
        const Pin LED = PIN(B, PB5);
    #endif

    // Controls activation of the keys, enabled when pulled down.
    const Pin ENABLE = PIN(C, PC0);
    
    // Charges the touch plates.
    const Pin SENDER = PIN(C, PC1);

    #define X(port, bit) PIN(port, bit),
    const Pin KEY_PINS[NUM_KEYS] = { KEY_LIST };
    #undef X
#endif

void boardSetup();
void boardLoop();
