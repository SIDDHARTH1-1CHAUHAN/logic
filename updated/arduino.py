#include <ArduinoJson.h>

// Pin Definitions (change these as per your wiring)
const int inputPinA = 2;
const int inputPinB = 3;
const int outputPin = 13;

// Variables for storing input and output
int inputA = 0;
int inputB = 0;
int output = 0;

void setup() {
  Serial.begin(9600);  // Start serial communication
  pinMode(inputPinA, INPUT);
  pinMode(inputPinB, INPUT);
  pinMode(outputPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String inputStr = Serial.readStringUntil('\n');  // Read the incoming JSON command
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, inputStr);

    if (error) {
      Serial.println("{\"status\": \"ERROR\", \"message\": \"Invalid JSON\"}");
      return;
    }

    String operation = doc["operation"];
    if (operation == "GATE") {
      String gateType = doc["gate_type"];
      JsonArray inputs = doc["inputs"].as<JsonArray>();
      
      inputA = inputs[0].as<int>();
      inputB = inputs[1].as<int>();
      
      if (gateType == "AND") {
        output = (inputA && inputB);
      } 
      else if (gateType == "OR") {
        output = (inputA || inputB);
      } 
      else if (gateType == "XOR") {
        output = (inputA != inputB);
      } 
      else if (gateType == "NAND") {
        output = !(inputA && inputB);
      } 
      else if (gateType == "NOR") {
        output = !(inputA || inputB);
      } 
      else if (gateType == "XNOR") {
        output = (inputA == inputB);
      } 
      else if (gateType == "NOT") {
        output = !inputA;  // Only one input for NOT gate
      }

      digitalWrite(outputPin, output);  // Set the output pin based on the result

      // Send the response back to Python
      String response = "{\"status\": \"OK\", \"output\": " + String(output) + "}";
      Serial.println(response);
    } 
    else if (operation == "PING") {
      Serial.println("{\"status\": \"OK\", \"message\": \"PONG\"}");
    }
  }
}
