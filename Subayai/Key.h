/*
 * Key.h
 * Wrapper around reading key states.
 */

#if defined(__AVR_ATmega328P__)
    #include "Board.h"
    #include "Config.h"

    class Key {
        public:
        Key() = default;

        bool poll() {
            uint16_t cycles = readCapacitive();
            bool rawPressed = cycles > config->keyThresholds[index];

            if (rawPressed && !state) {
                if (!lastRaw) {
                    lastChange = micros();
                }

                if ((micros() - lastChange) >= config->debounceDelay) {
                    state = true;
                }
            } else if (!rawPressed) {
                state = false;
            }

            lastRaw = rawPressed;
            return state;
        }

        void bind(Pin boundPin, const Config& cfg, uint8_t keyIndex) {
            pin = boundPin;
            index = keyIndex;
            config = &cfg;
        }

        private:
        Pin pin;
        uint8_t index = 0;
        const Config* config = nullptr;

        bool lastRaw = false;
        bool state = false;
        uint32_t lastChange = 0;

        uint16_t readCapacitive() {
            // Attempt to discharge the plate.
            *pin.ddr |= pin.bit;
            *pin.port &= ~pin.bit;
            delayMicroseconds(config->dischargeDelays[index]);
            *pin.ddr &= ~pin.bit;

            // Start charging.
            *SENDER.port |= SENDER.bit;

            uint16_t cycles = 0;

            // See how long it takes for this pin to read HIGH.
            while (!(*pin.pin & pin.bit)) {
                if (++cycles > MAX_THRESHOLD) {
                    break;
                }
            }

            // Stop charging.
            *SENDER.port &= ~SENDER.bit;

            return cycles;
        }
    };
#endif
