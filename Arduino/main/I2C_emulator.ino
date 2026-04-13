# ----
#       Diese Skript emuliert den INA419 I2C Sensor, sodass Über Modus vom Motor Strom/Momentwerte angefragt
#       und mit den vorhandenen Skripten ausgewertet werden können
# ----

#
# Manuelles "Bit-Banging" da SCL und SDA Pin hardware ACK, also einen 2. Teilnehmer benötigen.
# Zuerst wird am Sensor der Pointer auf das Messwert-Register gesetzt und dieses dann ausgelesen (2x write)
# Der gelesene Wert wird in 2 Bytes Eingelesen (Most- und Least-significant bit)
#

#define SDA_PIN 3
#define SCL_PIN 4
#define I2C_HALF_PERIOD_US 20
#define I2C_ADDRESS 0x40  // must match what the script sees

void i2c_delay() { delayMicroseconds(I2C_HALF_PERIOD_US); }

void i2c_start() {
    digitalWrite(SDA_PIN, LOW);
    i2c_delay();
    digitalWrite(SCL_PIN, LOW);
    i2c_delay();
}

void i2c_repeated_start() {
    digitalWrite(SDA_PIN, HIGH);
    i2c_delay();
    digitalWrite(SCL_PIN, HIGH);
    i2c_delay();
    digitalWrite(SDA_PIN, LOW);
    i2c_delay();
    digitalWrite(SCL_PIN, LOW);
    i2c_delay();
}

void i2c_stop() {
    digitalWrite(SDA_PIN, LOW);
    i2c_delay();
    digitalWrite(SCL_PIN, HIGH);
    i2c_delay();
    digitalWrite(SDA_PIN, HIGH);
    i2c_delay();
}

void i2c_write_bit(uint8_t bit) {
    digitalWrite(SDA_PIN, bit ? HIGH : LOW);
    i2c_delay();
    digitalWrite(SCL_PIN, HIGH);
    i2c_delay();
    digitalWrite(SCL_PIN, LOW);
    i2c_delay();
}

void i2c_write_byte(uint8_t b) {
    for (int i = 7; i >= 0; i--) {
        i2c_write_bit((b >> i) & 1);
    }
    i2c_write_bit(0);  // fake ACK
}

// ── INA219-style current register read emulation ──────────────

void i2c_send_current(uint16_t raw_value) {
    uint8_t msb = (raw_value >> 8) & 0xFF;
    uint8_t lsb = raw_value & 0xFF;

    // Transaction 1: write register pointer 0x04
    i2c_start();
    i2c_write_byte((I2C_ADDRESS << 1) | 0x00);  // write
    i2c_write_byte(0x04);                        // current register pointer

    // Transaction 2: repeated start + read address + two data bytes
    i2c_repeated_start();
    i2c_write_byte((I2C_ADDRESS << 1) | 0x01);  // read bit set
    i2c_write_byte(msb);  // index+3 in the CSV
    i2c_write_byte(lsb);  // index+4 in the CSV
    i2c_stop();
}

void setup() {
    pinMode(SDA_PIN, OUTPUT);
    pinMode(SCL_PIN, OUTPUT);
    digitalWrite(SDA_PIN, HIGH);
    digitalWrite(SCL_PIN, HIGH);
}

void loop() {
    // To send a specific current in mA:
    // raw = mA / 0.1  (because current_LSB = 1e-4 A = 0.1 mA)
    // e.g. 80.4 mA → raw = 804 = 0x0324
    i2c_send_current(0x0324);  // → 80.4 mA
    delay(2);
}