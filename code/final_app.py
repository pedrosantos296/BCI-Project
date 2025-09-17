import socket
import json
import time
import asyncio
import joblib
import pandas as pd
from collections import deque
from kasa import SmartBulb

# === Parâmetros ===
SAMPLE_INTERVAL = 1.0
WINDOW_SIZE = 5 #windowing
COOLDOWN_SECONDS = 10
CONSISTENT_PREDICTIONS = 3 #nº de previsoes seguidas

# === Carregar modelo e encoder ===
modelo = joblib.load("modelo_treinado.joblib")
label_encoder = joblib.load("label_encoder.joblib") #tradutor de 0/1 

feature_names = ['attention', 'meditation', 'delta', 'theta', 'alpha', 'beta', 'gamma']

def extract_features(window_data):
    if not window_data:
        return None
    df = pd.DataFrame(window_data, columns=feature_names)
    return df.mean().values.tolist()

async def control_bulb(state_on: bool, bulb):
    try:
        await bulb.update()
        if state_on and not bulb.is_on:
            await bulb.turn_on()
            print("💡 Lâmpada ligada")
        elif not state_on and bulb.is_on:
            await bulb.turn_off()
            print("💡 Lâmpada desligada")
    except Exception as e:
        print(f"Erro no controlo da lâmpada: {e}")

def connect_to_mindwave():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 13854))
            config = json.dumps({"enableRawOutput": False, "format": "Json"}).encode('utf-8')
            s.send(config)
            print("A conectar ao Mindwave")
            return s
        except Exception as e:
            print(f"Erro ao conectar ao Mindwave: {e}. Tentando novamente em 5s...")
            time.sleep(5)

async def main():
    s = connect_to_mindwave()
    buffer = ""
    decoder = json.JSONDecoder()
    data_queue = deque()
    prediction_history = deque(maxlen=CONSISTENT_PREDICTIONS)

    last_action = None
    last_change_time = 0

    bulb = SmartBulb("172.20.10.13")  # IP da lâmpada

    try:
        while True:
            try:
                raw = s.recv(2048).decode('utf-8', errors='ignore')
                if not raw:
                    raise ConnectionError("Conexão fechada pelo Mindwave.")
                buffer += raw
            except Exception as e:
                print(f"Erro na recepção do Mindwave: {e}. Reconectando...")
                s.close()
                s = connect_to_mindwave()
                buffer = ""
                continue

            while buffer:
                buffer = buffer.lstrip()
                try:
                    obj, idx = decoder.raw_decode(buffer)
                    buffer = buffer[idx:]

                    if 'eegPower' in obj and 'eSense' in obj:
                        attention = obj['eSense'].get('attention', 0)
                        meditation = obj['eSense'].get('meditation', 0)
                        eeg = obj['eegPower']
                        delta = eeg.get("delta", 0)
                        theta = eeg.get("theta", 0)
                        alpha = eeg.get("lowAlpha", 0) + eeg.get("highAlpha", 0)
                        beta = eeg.get("lowBeta", 0) + eeg.get("highBeta", 0)
                        gamma = eeg.get("lowGamma", 0) + eeg.get("highGamma", 0)

                        timestamp = time.time()
                        data_queue.append((
                            timestamp, attention, meditation, delta, theta, alpha, beta, gamma
                        ))
                        # Remove dados mais antigos que 5 segundos:
                        while data_queue and (timestamp - data_queue[0][0] > WINDOW_SIZE):
                            data_queue.popleft()

                        window_features = [d[1:] for d in data_queue]
                        features_mean = extract_features(window_features)

                        if features_mean:
                            features_df = pd.DataFrame([features_mean], columns=feature_names)
                            pred = modelo.predict(features_df)[0]
                            estado = label_encoder.inverse_transform([pred])[0]
                            print(f"[{time.strftime('%H:%M:%S')}] Previsão: {estado}")

                            prediction_history.append(pred)

                            if (len(prediction_history) == CONSISTENT_PREDICTIONS and
                                all(p == pred for p in prediction_history) and
                                pred != last_action and
                                time.time() - last_change_time >= COOLDOWN_SECONDS):

                                await control_bulb(state_on=(pred == 0), bulb=bulb)
                                last_action = pred
                                last_change_time = time.time()

                except json.JSONDecodeError:
                    break

            await asyncio.sleep(SAMPLE_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 Interrompido pelo utilizador.")
    finally:
        s.close()

if __name__ == "__main__":
    asyncio.run(main())
