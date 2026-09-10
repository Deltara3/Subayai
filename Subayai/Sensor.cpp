/*
 * Sensor.cpp
 * Reads the touch plates and sends the state data to the bridge.
 */

#if defined(__AVR_ATmega328P__)
    #include "Board.h"
    #include "Config.h"
    #include "Protocol.h"
    #include "Key.h"
    
    Config config;
    Key keys[NUM_KEYS] = { Key() };
    uint16_t lastSent = 0x0000;

    void boardSetup() {
        Serial.begin(BAUD_RATE);

        // Set enable pin to INPUT and enable pull-up.
        *ENABLE.ddr &= ~ENABLE.bit;
        *ENABLE.port |= ENABLE.bit;

        // Set sender to OUTPUT.
        *SENDER.ddr |= SENDER.bit;

        // Set recievers to INPUT.
        for (uint8_t i = 0; i < NUM_KEYS; i++) {
            *KEY_PINS[i].ddr &= ~KEY_PINS[i].bit;
        }

        #if defined(LED_WARNING)
            // Set LED to OUTPUT.
            *LED.ddr |= LED.bit;
        #endif

        bool hasConfig = false;

        // Try to get initial config.
        while (!hasConfig) {
            Protocol::requestConfig(Serial);

            #if defined(LED_WARNING)
                *LED.pin = LED.bit;
            #endif

            uint8_t cmd = 0;

            if (Serial.readBytes(&cmd, 1) == 1 && cmd == CMD_CONFIG_UPDATE) {
                hasConfig = Protocol::readConfig(Serial, config);
            }
        }

        #if defined(LED_WARNING)
            // Force LED back on.
            *LED.port |= LED.bit;
        #endif

        // Bind keys to obtained config.
        for (uint8_t i = 0; i < NUM_KEYS; i++) {
            keys[i].bind(KEY_PINS[i], config, i);
        }
    }

    void boardLoop() {
        // Handle any requests from Bridge.
        if (Serial.available() > 0) {
            uint8_t cmd = Serial.read();

            // Yes, I don't need a switch but it's future proofing.
            switch (cmd) {
                case CMD_CONFIG_UPDATE: {
                    Protocol::readConfig(Serial, config);
                    lastSent = 0x0000;
                    break;
                }
            }
        }

        uint16_t packedKeys = 0;
        bool enabled = !(*ENABLE.pin & ENABLE.bit);

        // Poll each key.
        if (enabled) {
            for (uint8_t i = 0; i < NUM_KEYS; i++) {
                packedKeys |= keys[i].poll() << i;
            }
        }

        // Send to Bridge if needed.
        if (packedKeys != lastSent) {
            Protocol::sendKeyState(Serial, packedKeys);
            lastSent = packedKeys;
        }
    }
#endif
