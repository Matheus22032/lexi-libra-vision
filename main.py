import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def calcular_angulo(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a ** 2 for a in v1))
    mag2 = math.sqrt(sum(b ** 2 for b in v2))
    if mag1 * mag2 == 0:
        return 0
    cos_theta = dot / (mag1 * mag2)
    angulo = math.degrees(math.acos(min(1.0, max(-1.0, cos_theta))))
    return angulo

def get_finger_states(landmarks):
    dedos = []

    if landmarks[4].x < landmarks[3].x:
        dedos.append(1)
    else:
        dedos.append(0)

    for tip in [8, 12, 16, 20]:
        if landmarks[tip].y < landmarks[tip - 2].y:
            dedos.append(1)
        else:
            dedos.append(0)

    return dedos

def reconhecer_letra(dedos,landmarks, movimento=False, angulo_entre_dedos=None):
    alfabeto_simplificado = {
        (1, 0, 0, 0, 0): "A", 
        (0, 1, 1, 1, 1): "B",  
        (0, 1, 0, 0, 0): "D",  
        (0, 0, 0, 0, 0): "E",  
        (1, 0, 1, 1, 1): "F",  
        (0, 0, 0, 0, 1): "I", 
        (1, 1, 0, 0, 0): "L",  
        (0, 0, 1, 1, 1): "T",  
        (1, 0, 0, 0, 1): "Y",  
        (0, 1, 1, 1, 0): "W"  
    }

    key = tuple(dedos)

    if key == (0, 1, 1, 0, 0):
        if angulo_entre_dedos is not None:
            if angulo_entre_dedos < 10:
                return "U"
            elif angulo_entre_dedos > 10:
                return "V"
            else:
                return "?" 
        else:
            return "U"  
        

    if key == (1, 1, 0, 0, 0):
        if angulo_entre_dedos is not None:
            if angulo_entre_dedos > 40:
                return "L"
            else:
                return "G"


    return alfabeto_simplificado.get(key, "?")


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    if resultado.multi_hand_landmarks:
        for mao in resultado.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, mao, mp_hands.HAND_CONNECTIONS)

            estados = get_finger_states(mao.landmark)

            angulo_entre_dedos = None
            if estados == [0, 1, 1, 0, 0]:
                indice_tip = mao.landmark[8]
                indice_mcp = mao.landmark[5]
                medio_tip = mao.landmark[12]
                medio_mcp = mao.landmark[9]

                vetor_indice = (
                    indice_tip.x - indice_mcp.x,
                    indice_tip.y - indice_mcp.y,
                    indice_tip.z - indice_mcp.z
                )

                vetor_medio = (
                    medio_tip.x - medio_mcp.x,
                    medio_tip.y - medio_mcp.y,
                    medio_tip.z - medio_mcp.z
                )

                angulo_entre_dedos = calcular_angulo(vetor_indice, vetor_medio)

            if estados == [1, 1, 0, 0, 0]:
                polegar_tip = mao.landmark[4]
                polegar_mcp = mao.landmark[2]


                indicador_tip = mao.landmark[8]
                indicador_mcp = mao.landmark[6]

                vetor_polegar = (
                    polegar_tip.x - polegar_mcp.x,
                    polegar_tip.y - polegar_mcp.y,
                    polegar_tip.z - polegar_mcp.z
                )
                vetor_indicador = (
                    indicador_tip.x - indicador_mcp.x,
                    indicador_tip.y - indicador_mcp.y,
                    indicador_tip.z - indicador_mcp.z
                )

                angulo_entre_dedos = calcular_angulo(vetor_polegar, vetor_indicador)

            letra = reconhecer_letra(estados,mao.landmark, angulo_entre_dedos=angulo_entre_dedos)

            cv2.putText(frame, f"Letra: {letra}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
            

    cv2.imshow("Lexi - Reconhecimento de LIBRAS", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
