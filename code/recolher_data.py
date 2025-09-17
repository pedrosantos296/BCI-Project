import socket
import json
import csv
import time
import os

HOST = '127.0.0.1'
PORT = 13854
DURATION = 300  # segundos

label = input("Indica a label desta sessão (concentrado / relaxado): ")

def connect_to_tgc():
    print("[DEBUG] Conectando ao TGC...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    config = json.dumps({
        "enableRawOutput": False,
        "format": "Json"
    })
    s.sendall(config.encode('utf-8'))
    print("[DEBUG] Configuração enviada ao TGC.")
    time.sleep(1)
    return s

def read_and_save(filename):
    os.makedirs('data', exist_ok=True)

    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            writer.writerow(["timestamp", "attention", "meditation", "delta", "theta", "alpha", "beta", "gamma", "label"])

        s = connect_to_tgc()
        start_time = time.time()
        buffer = ""
        decoder = json.JSONDecoder()

        while time.time() - start_time < DURATION:
            try:
                raw = s.recv(2048).decode('utf-8', errors='ignore')
                buffer += raw

                while buffer:
                    buffer = buffer.lstrip()
                    try:
                        obj, idx = decoder.raw_decode(buffer)
                        buffer = buffer[idx:]

                        if 'eegPower' in obj and 'eSense' in obj:
                            timestamp = time.time()
                            attention = obj['eSense'].get('attention', 0)
                            meditation = obj['eSense'].get('meditation', 0)
                            eeg = obj['eegPower']

                            writer.writerow([
                                timestamp,
                                attention,
                                meditation,
                                eeg.get("delta", 0),
                                eeg.get("theta", 0),
                                eeg.get("lowAlpha", 0) + eeg.get("highAlpha", 0),
                                eeg.get("lowBeta", 0) + eeg.get("highBeta", 0),
                                eeg.get("lowGamma", 0) + eeg.get("highGamma", 0),
                                label
                            ])
                            print(f"[DEBUG] CSV: attention={attention}, meditation={meditation}")
                        else:
                            print("[DEBUG] JSON ignorado, faltam campos.")

                    except json.JSONDecodeError:
                        break

            except socket.error as e:
                print(f"[ERRO] Erro de socket: {e}")
                break

        s.close()
        print("[DEBUG] Conexão fechada. Dados salvos em:", filename)

if __name__ == "__main__":
    read_and_save('data/onda_real.csv')
