import cv2
import mediapipe as mp
import serial
import time
import sys

# Inicializar MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
)

# Configuración de comunicación serial
def init_serial(port):
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Espera para estabilizar
        print(f"✔ Conexión establecida en {port}")
        return arduino
    except Exception as e:
        print(f"✖ Error al conectar con Arduino: {e}")
        return None

# Función mejorada para contar dedos
def count_fingers(hand_landmarks):
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    
    finger_count = 0
    
    # Contar dedos (excepto pulgar)
    for tip in finger_tips:
        tip_pos = hand_landmarks.landmark[tip]
        dip_pos = hand_landmarks.landmark[tip - 2]  # Articulación DIP
        if tip_pos.y < dip_pos.y:
            finger_count += 1
    
    # Detección de pulgar
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    
    # Determinar mano izquierda/derecha
    if hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x < thumb_tip.x:
        if thumb_tip.x > thumb_ip.x:  # Mano izquierda
            finger_count += 1
    else:
        if thumb_tip.x < thumb_ip.x:  # Mano derecha
            finger_count += 1
    
    return min(finger_count, 5)  # Máximo 5 dedos

# Función principal 
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✖ Error: No se pudo acceder a la cámara")
        sys.exit(1)
    
    arduino = init_serial('COM3')  # Cambiar al puerto correcto
    previous_fingers = -1
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue
        
        # Procesamiento de imagen
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        current_fingers = 0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar landmarks (sintaxis corregida)
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
                current_fingers = count_fingers(hand_landmarks)
        
        # Mostrar conteo
        cv2.putText(image, f"Dedos: {current_fingers}", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Enviar a Arduino si cambió el conteo
        if arduino and current_fingers != previous_fingers:
            try:
                arduino.write(f"{current_fingers}".encode())
                print(f"📤 Enviado: {current_fingers}")
                previous_fingers = current_fingers
            except Exception as e:
                print(f"⚠ Error de comunicación: {e}")
                arduino = None
        
        cv2.imshow('Contador de Dedos', image)
        
        # Salir con ESC o 'q'
        if cv2.waitKey(10) & 0xFF in (27, ord('q')):
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()
    print("🔌 Programa terminado correctamente")

if __name__ == "__main__":
    main()