// Define pins for inputs A and B
const int inputPinA = 22; // Pin for input A
const int inputPinB = 24; // Pin for input B

// Define pin for the output of the logic gate (for simulation)
const int outputPin = 26; // Pin for output (LED or logic gate output indicator)

String gateType = "AND"; // Default gate type (initially AND)

void setup() {
  // Initialize input pins
  pinMode(inputPinA, INPUT);
  pinMode(inputPinB, INPUT);
  
  // Initialize output pin (LED or indicator)
  pinMode(outputPin, OUTPUT);
  
  // Start serial communication
  Serial.begin(9600);
  
  // Give some time for the serial connection to establish
  delay(2000);
}

void loop() {
  // Read the input values (either HIGH or LOW)
  int inputA = digitalRead(inputPinA); 
  int inputB = digitalRead(inputPinB);

  // Check if there is any new serial input (select new gate operation)
  if (Serial.available() > 0) {
    gateType = Serial.readStringUntil('\n'); // Read until newline character
    gateType.trim(); // Remove any extra whitespace/newline
    Serial.print("Selected Gate: ");
    Serial.println(gateType); // Output selected gate for debugging
  }

  // Determine the logic gate output based on the selected gate
  int output = 0; // Default value (OFF)
  
  if (gateType == "AND") {
    output = inputA && inputB; // AND gate
  }
  else if (gateType == "OR") {
    output = inputA || inputB; // OR gate
  }
  else if (gateType == "NOT") {
    output = !inputA; // NOT gate (only uses input A)
  }
  else if (gateType == "XOR") {
    output = inputA ^ inputB; // XOR gate
  }
  else if (gateType == "NAND") {
    output = !(inputA && inputB); // NAND gate
  }
  else if (gateType == "NOR") {
    output = !(inputA || inputB); // NOR gate
  }
  else if (gateType == "XNOR") {
    output = !(inputA ^ inputB); // XNOR gate
  }
  
  // Write output value to output pin (LED or indicator)
  digitalWrite(outputPin, output); // Turn the output LED on or off

  // Send the result to the serial monitor (or PC)
  Serial.println(output); // Output either 1 or 0

  // Wait for a short period before reading inputs again
  delay(500); // 500 ms delay
}
