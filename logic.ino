#define INPUT1 2  // Connect push button or digital input to pin 2
#define INPUT2 3  // Connect push button or digital input to pin 3
#define OUTPUT_LED 4 // LED or other output device

void setup() {
    Serial.begin(9600);   // Start Serial communication
    pinMode(INPUT1, INPUT_PULLUP);  // Enable internal pull-up resistors
    pinMode(INPUT2, INPUT_PULLUP);
    pinMode(OUTPUT_LED, OUTPUT);
}

void loop() {
    int in1 = !digitalRead(INPUT1);  // Read inputs (invert because of pull-ups)
    int in2 = !digitalRead(INPUT2);

    Serial.print(in1);  // Send input 1 over Serial
    Serial.print(",");
    Serial.println(in2);  // Send input 2 over Serial

    // Wait for response from Python (Streamlit app)
    while (Serial.available() == 0) {
        // Wait until data is received
    }

    int outputValue = Serial.parseInt(); // Read the computed output
    digitalWrite(OUTPUT_LED, outputValue);  // Set LED based on result

    delay(500); // Small delay to avoid flooding serial communication
}
