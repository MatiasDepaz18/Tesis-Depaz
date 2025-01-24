import cv2

# Inicializar la cámara (0 es para la cámara por defecto)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error al abrir la cámara")
    exit()

while True:
    # Leer un frame de la cámara
    ret, frame = cap.read()

    if not ret:
        print("No se pudo recibir el frame. Saliendo...")
        break

    # Mostrar el frame en una ventana
    cv2.imshow('Camara', frame)

    # Salir del bucle al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
