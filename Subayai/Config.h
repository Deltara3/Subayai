/*
 * Config.h
 * Defines values that can be altered at runtime.
 */

#pragma once

#if defined(__AVR_ATmega16U2__)
#include <EEPROM.h>
#include "HID-Project.h"
#endif

#include "Board.h"

// Change this if you already have EEPROM data at this location.
constexpr uint16_t CONFIG_ADDR = 0x0000;

// Default settings.
constexpr uint16_t DEFAULT_THRESHOLD = 30;
constexpr uint16_t DEFAULT_DISCHARGE_DELAY = 30;
constexpr uint16_t DEFAULT_DEBOUNCE = 0;

// You can touch this but there won't be much benefit.
constexpr uint16_t MAX_DISCHARGE_DELAY = 5000;
constexpr uint16_t MAX_THRESHOLD = 1000;
constexpr uint16_t MAX_DEBOUNCE = 50000;

class __attribute__((packed)) Config {
    public:
    uint8_t keyCodes[MAX_KEYS];
    uint16_t keyThresholds[MAX_KEYS];
    uint16_t dischargeDelays[MAX_KEYS];
    uint16_t debounceDelay;

    #if defined(__AVR_ATmega16U2__)
        void defaults() {
            debounceDelay = DEFAULT_DEBOUNCE;
    
            for (uint8_t i = 0; i < MAX_KEYS; i++) {
                keyCodes[i] = KEY_RESERVED;
                dischargeDelays[i] = DEFAULT_DISCHARGE_DELAY;
                keyThresholds[i] = DEFAULT_THRESHOLD;
            }
        }

        void load() {
            EEPROM.get(CONFIG_ADDR, *this);
        }

        void save() const {
            EEPROM.put(CONFIG_ADDR, *this);
        }

        bool validate() const {
            if (debounceDelay > MAX_DEBOUNCE) {
                return false;
            }

            for (uint8_t i = 0; i < MAX_KEYS; i++) {
                if (keyThresholds[i] == 0 || keyThresholds[i] > MAX_THRESHOLD) {
                    return false;
                }

                if (dischargeDelays[i] == 0 || dischargeDelays[i] > MAX_DISCHARGE_DELAY) {
                    return false;
                }

                if (!validKey(keyCodes[i])) {
                    return false;
                }
            }

            return true;
        }
    #endif

    private:
    #if defined(__AVR_ATmega16U2__)
        bool validKey(uint8_t key) const {
            switch (key) {
                case KEY_RESERVED:
                case KEY_A ... KEY_APPLICATION:
                case KEY_POWER ... KEY_EXSEL:
                case KEY_PAD_00 ... KEYPAD_HEXADECIMAL:
                case KEY_LEFT_CTRL ... KEY_RIGHT_GUI:
                    return true;
                default:
                    return false;
            }
        }
    #endif
};
