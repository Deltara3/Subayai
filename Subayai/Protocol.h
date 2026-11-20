/*
 * Protocol.h
 * Defines the Serial communication between the Bridge, Sensor, and the host.
 */

#pragma once

#include "Board.h"
#include "Config.h"

enum Command: uint8_t {
    CMD_ACK = 0x01,
    CMD_NAK = 0x02,
    CMD_KEY_COUNT = 0x10,
    CMD_CONFIG_REQUEST = 0x20,
    CMD_CONFIG_UPDATE = 0x21,
    CMD_CONFIG_RESET = 0x22,
    CMD_KEY_STATE = 0x30,
    CMD_SENSE_START = 0x31,
    CMD_SENSE_STOP = 0x32,
    CMD_SENSE_REQUEST = 0x33,
    CMD_SENSE_STATE = 0x34
};

class Protocol {
    public:
    #if defined(__AVR_ATmega16U2__)
        static void sendAck(Stream& serial) {
            serial.write(CMD_ACK);
        }

        static void sendNak(Stream& serial) {
            serial.write(CMD_NAK);
        }

        static void sendConfig(Stream& serial, const Config& config) {
            serial.write(CMD_CONFIG_UPDATE);
            serial.write((const uint8_t*)&config, sizeof(Config));
            serial.flush();

            // Clear RX of any duplicate config requests.
            while (serial.available() > 0 && serial.peek() == CMD_CONFIG_REQUEST) {
                serial.read();
            }
        }

        static uint16_t readKeyState(Stream& serial) {
            uint16_t packedKeys = 0;
            serial.readBytes((uint8_t*)&packedKeys, sizeof(packedKeys));
            return packedKeys;
        }

        static void sendKeyCount(Stream& serial, uint8_t count) {
            serial.write(CMD_KEY_COUNT);
            serial.write(count);
        }

        static void enterSense(Stream& serial) {
            serial.write(CMD_SENSE_START);
        }

        static void leaveSense(Stream& serial) {
            serial.write(CMD_SENSE_STOP);
        }

        static void requestSense(Stream& serial) {
            serial.write(CMD_SENSE_REQUEST);
        }

        static bool readSenseState(Stream& serial, uint16_t* state) {
            return serial.readBytes((uint8_t*)state, sizeof(uint16_t) * MAX_KEYS) == sizeof(uint16_t) * MAX_KEYS;
        }
    #endif

    #if defined(__AVR_ATmega328P__)
        static void requestConfig(Stream& serial) {
            serial.write(CMD_CONFIG_REQUEST);
        }

        static void sendKeyState(Stream& serial, uint16_t packedKeys) {
            serial.write(CMD_KEY_STATE);
            serial.write((const uint8_t*)&packedKeys, sizeof(packedKeys));
        }
    #endif

    static bool readConfig(Stream& serial, Config& config) {
        return serial.readBytes((uint8_t*)&config, sizeof(Config)) == sizeof(Config);
    }

    static void sendSenseState(Stream& serial, const uint16_t* state) {
        serial.write(CMD_SENSE_STATE);
        serial.write((const uint8_t*)state, sizeof(uint16_t) * MAX_KEYS);
    }
};
