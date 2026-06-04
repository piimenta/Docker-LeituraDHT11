import serial
import requests
import time

# ==========================================
# CONFIGURAÇÕES (Altere para o seu cenário)
# ==========================================
PORTA_COM = 'COM3'
BAUD_RATE = 9600
IP_SERVIDOR = '192.168.169.27'   # IP do PC servidor (Ubuntu) na rede Wi-Fi
URL_TELEGRAF = f'http://{IP_SERVIDOR}:8081/arduino'

try:
    # 1. Abre a comunicação com o Arduino via USB
    arduino = serial.Serial(PORTA_COM, BAUD_RATE)
    print(f"🔌 Conectado no Arduino pela porta {PORTA_COM}.")
    print(f"📡 Preparado para enviar dados para a rede: {URL_TELEGRAF}")
    time.sleep(2) # Tempo para o DHT11 estabilizar
    
    while True:
        # 2. Fica escutando se o Arduino mandou algo
        if arduino.in_waiting > 0:
            linha = arduino.readline().decode('utf-8').strip()
            
            if linha == "Erro":
                print("Falha na leitura do sensor DHT11!")
                continue
            
            try:
                # 3. Converte a leitura do cabo USB para número
                temperatura = float(linha)
                
                # 4. Formata no padrão InfluxDB (Usando a tabela 'ambiente' do seu Código 1)
                dado_formatado = f"ambiente,sensor=DHT11,pino=D4 temperatura={temperatura}"
                
                # 5. Dispara para a rede via Wi-Fi (Usando a lógica do seu Código 2)
                resposta = requests.post(URL_TELEGRAF, data=dado_formatado, timeout=3)
                
                if resposta.status_code == 204:
                    print(f"[SUCESSO] Dado real enviado: {temperatura}°C | Destino: {IP_SERVIDOR}")
                else:
                    print(f"[ERRO HTTP] O Servidor retornou o código: {resposta.status_code}")
                    
            except ValueError:
                # Se o Arduino mandar algum "lixo" pela porta serial, o script avisa em vez de ignorar calado
                print(f"[AVISO] O Arduino enviou texto que não pode ser convertido: '{linha}'")
                
            except requests.exceptions.RequestException:
                # Se o cabo de rede ou Wi-Fi cair, avisa aqui
                print(f"[FALHA DE REDE] Destino inalcançável. O servidor no IP {IP_SERVIDOR} está ligado?")

except serial.SerialException:
    print(f"Erro: Não foi possível abrir a porta {PORTA_COM}. O cabo está solto ou o Monitor Serial está aberto?")
except Exception as e:
    print(f"Erro geral: {e}")