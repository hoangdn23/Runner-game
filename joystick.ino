// int x = A0;
int y = A1;
int button = 2;
// int x_val;
int y_val;
int button_state;

void setup() {
  Serial.begin(9600);
  // pinMode(x, INPUT);
  pinMode(y, INPUT);
  pinMode(button, INPUT_PULLUP);
}

void loop() {
  // x_val = analogRead(x);
  y_val = analogRead(y);
  button_state = digitalRead(button);

  // Serial.print("X: ");
  // Serial.print(x_val);
  Serial.print(y_val);
  Serial.print(" ");
  Serial.println(button_state);

  delay(10);
}