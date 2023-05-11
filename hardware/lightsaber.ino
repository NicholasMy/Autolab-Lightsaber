#include <FastLED.h>
#include <WiFiClient.h>
#include <ESP8266WiFi.h>
#include "WebSocketClient.h"
#include <ArduinoJson.h>

#define NUM_LEDS 168 // The COUNT of physical LEDS on the strip. Not the highest index. Not the number of virtual LEDs.
// #define LED_PIN 2  // D4
#define LED_PIN 5  // D1
// #define LED_PIN 1 // TX
#define BRIGHTNESS 3
#define LED_TYPE WS2811
#define COLOR_ORDER GRB
CRGB led_strip[NUM_LEDS];

const char host[] = "napps.cse.buffalo.edu";
const char path[] = "/ws";
const int wsPort = 6334;
const char *wirelessSsid = "UB_Devices";
const char *wirelessPassword = "goubbulls";

// WebSocket example https://github.com/arduino-libraries/ArduinoHttpClient/blob/6dc486747820d6544b41747c68c6b748f888d661/examples/SimpleWebSocket/SimpleWebSocket.ino
WiFiClient wifiClient;
WebSocketClient ws(true);

// Set the points on the LED strip where it folds to change directions
const int LED_FOLD_1 = 55;  // Absolute index where the LED strip folds for the first time
const int LED_FOLD_2 = LED_FOLD_1 * 2;
const int FINAL_LED = LED_FOLD_1 * 3;

int getPhysicalLedNumber(int logicalLedNumber) {
  // Given a "logical LED number" (as if the lightsaber were one continuous strip of LEDs without folds)
  // return the actual LED index on the folded LED strip

  int remainder = logicalLedNumber % 3;

  if (remainder == 0) {
    // Belongs to first segment
    return logicalLedNumber / 3;
  } else if (remainder == 1) {
    // Belongs to second segment, which is reversed
    return LED_FOLD_2 - (logicalLedNumber / 3);
  } else if (remainder == 2) {
    // Belongs to third segment
    return LED_FOLD_2 + (logicalLedNumber / 3) + 3;  // This skips 2 LEDs on the bottom to give space for the LED strip to wrap
  }
  return 0;  // It must match one of the above, but this is required.
}

void clearLedStrip() {
  // Turn off all the LEDs
  fill_solid(led_strip, NUM_LEDS, CRGB::Black);
  FastLED.show();
}

void dataReceivedFromWebSocket(String &data) {
  // Serial.println("------- New message ---------");
  const char *json = data.c_str();
  DynamicJsonDocument doc(12300); // This is about as large as I can go without raising an exception
  deserializeJson(doc, json);

  JsonObject root = doc.as<JsonObject>();

  for (JsonPair kv : root) {
    const char *key = kv.key().c_str();
    if (strcmp(key, "brightness") == 0) {
      // Serial.print("BRIGHTNESS: ");
      int brightness = kv.value().as<int>();
      // Serial.println(brightness);
      FastLED.setBrightness(brightness);
    } else {
      int ledIndex = getPhysicalLedNumber(atoi(key));
      int colorRed = kv.value()[0];
      int colorGreen = kv.value()[1];
      int colorBlue = kv.value()[2];
      // Serial.print("LED INDEX: ");
      // Serial.println(ledIndex);
      // Serial.print("color value: ");
      // Serial.print(colorRed);
      // Serial.print(", ");
      // Serial.print(colorGreen);
      // Serial.print(", ");
      // Serial.println(colorBlue);
      led_strip[ledIndex].red = colorRed;
      led_strip[ledIndex].green = colorGreen;
      led_strip[ledIndex].blue = colorBlue;
    }
  }
  FastLED.delay(10);
}

void ensureWiFiConnected() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(wirelessSsid, wirelessPassword);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.println("Reconnecting to WiFi");
      Serial.print(".");
      delay(200);
    }
  }
}


void setup() {
  // Set up LED strip
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(led_strip, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  clearLedStrip();

  // Set up Wi-Fi
  ensureWiFiConnected();

  delay(500);  // Wait to start serial output to reduce errors
  Serial.begin(9600);
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  ensureWiFiConnected();

  if (!ws.isConnected()) {
    Serial.println("Reconnecting to websocket");
    ws.connect(host, path, wsPort);
    if (ws.isConnected()) {
      Serial.println("Connected to websocket!");
    }
  } else {
    String msg;
    if (ws.getMessage(msg)) {
      dataReceivedFromWebSocket(msg);
    }
  }
}
