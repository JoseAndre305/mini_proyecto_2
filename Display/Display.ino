// Configuración de pines para cada segmento
const int segmentPins[] = {2, 3, 4, 5, 6, 7, 8}; // a, b, c, d, e, f, g

// Patrones para números 0-5 (cátodo común)
const byte digitPatterns[6][7] = {
  {1, 1, 1, 1, 1, 1, 0}, // 0
  {0, 1, 1, 0, 0, 0, 0}, // 1
  {1, 1, 0, 1, 1, 0, 1}, // 2
  {1, 1, 1, 1, 0, 0, 1}, // 3
  {0, 1, 1, 0, 0, 1, 1}, // 4
  {1, 0, 1, 1, 0, 1, 1}  // 5
};

void setup() {
  Serial.begin(9600);
  // Configurar todos los pines como salidas
  for (int i = 0; i < 7; i++) {
    pinMode(segmentPins[i], OUTPUT);
  }
  Serial.println("Sistema listo. Esperando datos...");
}

void loop() {
  if (Serial.available() > 0) {
    int fingerCount = Serial.read() - '0'; // Convertir char a int
    
    if (fingerCount >= 0 && fingerCount <= 5) {
      displayNumber(fingerCount);
      Serial.print("Mostrando: ");
      Serial.println(fingerCount);
    }
  }
}

// Función para mostrar número en el display
void displayNumber(int num) {
  for (int i = 0; i < 7; i++) {
    digitalWrite(segmentPins[i], digitPatterns[num][i]);
  }
}