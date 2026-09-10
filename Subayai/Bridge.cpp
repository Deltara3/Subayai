/*
 * Bridge.cpp
 * Handles config and keyboard emulation.
 */
 
#if defined(__AVR_ATmega16U2__)
    #include "Board.h"
    #include "Config.h"
    #include "Protocol.h"
    #include "HID-Project.h"

    Config config;
    bool lastKeys[NUM_KEYS] = { false };

    void boardSetup() {
        Serial.begin(BAUD_RATE);
        Serial1.begin(BAUD_RATE);

        config.load();

        // If the config was missing or corrupted, load defaults.
        if (!config.validate()) {
            config.defaults();
            config.save();
        }

        NKROKeyboard.begin();
    }

    void boardLoop() {
        // Handle any requests from the host.
        if (Serial.available() > 0) {
            uint8_t cmd = Serial.read();

            switch (cmd) {
                case CMD_CONFIG_REQUEST: {
                    Protocol::sendConfig(Serial, config);
                    break;
                }
                case CMD_CONFIG_UPDATE: {
                    if (Protocol::readConfig(Serial, config) && config.validate()) {
                        config.save();
                        Protocol::sendConfig(Serial1, config);
                        Protocol::sendAck(Serial);
                    } else {
                        config.load();
                        Protocol::sendNak(Serial);
                    }

                    NKROKeyboard.releaseAll();
                    memset(lastKeys, false, sizeof(lastKeys));
                    break;
                }
                case CMD_CONFIG_RESET: {
                    config.defaults();
                    config.save();
                    
                    Protocol::sendConfig(Serial1, config);
                    Protocol::sendAck(Serial);

                    NKROKeyboard.releaseAll();
                    memset(lastKeys, false, sizeof(lastKeys));
                    break;
                }
                case CMD_KEY_COUNT: {
                    Protocol::sendKeyCount(Serial, NUM_KEYS);
                    break;
                }
            }
        }

        // Handle any requests from Sensor.
        if (Serial1.available() > 0) {
            uint8_t cmd = Serial1.read();

            switch (cmd) {
                case CMD_CONFIG_REQUEST: {
                    Protocol::sendConfig(Serial1, config);
                    break;
                }
                case CMD_KEY_STATE: {
                    uint16_t packedKeys = Protocol::readKeyState(Serial1);

                    for (uint8_t i = 0; i < NUM_KEYS; i++) {
                        bool currentKey = ((packedKeys >> i) & 1) == 1;

                        if (currentKey != lastKeys[i] && config.keyCodes[i] != KEY_RESERVED) {
                            if (currentKey) {
                                NKROKeyboard.add((KeyboardKeycode)config.keyCodes[i]);
                            } else {
                                NKROKeyboard.remove((KeyboardKeycode)config.keyCodes[i]);
                            }

                            lastKeys[i] = currentKey;
                        }
                    }

                    NKROKeyboard.send();
                    break;
                }
            }
        }
    }
#endif
