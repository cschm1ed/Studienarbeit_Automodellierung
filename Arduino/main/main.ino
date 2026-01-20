#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;
extern TwoWire Wire;

#define PIN_STATUS_LED 2 // Status LED die ausgeschaltet wird wenn der Arduino auf Antwort des Sensor wartet.

void setup(void) {
  Serial.begin(115200);
  while (!Serial);

  Wire.begin();
  Wire.setWireTimeout(10000, true); // timeout nach 10000 microsekunden -> 10 ms -- reset I2c on timeout = true

  if (!ina219.begin()) {
    Serial.println("Kein INA219-Sensor gefunden.");
    while (1);
  }

  ina219.setCalibration_32V_2A();
  pinMode(PIN_STATUS_LED, OUTPUT);
}

void loop(void) {
  digitalWrite(PIN_STATUS_LED, LOW);
  float current_mA = ina219.getCurrent_mA();
  digitalWrite(PIN_STATUS_LED, HIGH);

  if (current_mA > 2000) {
    Serial.println("Ueberhitzung erkannt!");
  } else {
    Serial.println(current_mA);
  }

  //delay(10);
}