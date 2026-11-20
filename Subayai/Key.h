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


        uint16_t readCapacitive() {
            // Give the plate a moment to discharge completely.
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

            // Prevent this plate from feeding other plates.
            *pin.ddr |= pin.bit;

            return cycles;
        }

        private:
        Pin pin;
        uint8_t index = 0;
        const Config* config = nullptr;

        bool lastRaw = false;
        bool state = false;
        uint32_t lastChange = 0;
    };
#endif
