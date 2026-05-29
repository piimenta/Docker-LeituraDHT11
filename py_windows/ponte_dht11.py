import serial
import requests
import time

PORTA_COM = 'COM3'  # <--- ALTERE AQUI SE NECESSÁRIO
BAUD_RATE = 9600
URL_TELEGRAF = 'http://localhost:8080/arduino'

try:
    arduino = serial.Serial(PORTA_COM, BAUD_RATE)
    print(f"Conectado na {PORTA_COM}. Aguardando DHT11 (2 segundos)...")
    time.sleep(2) 
    
    while True:
        if arduino.in_waiting > 0:
            linha = arduino.readline().decode('utf-8').strip()
            
            if linha == "Erro":
                print("Falha na leitura do sensor DHT11!")
                continue
            
            try:
                temperatura = float(linha)
                # Formato que o Telegraf exige: tabela,tags valor
                dado_formatado = f"ambiente,sensor=DHT11,pino=D4 temperatura={temperatura}"
                
                resposta = requests.post(URL_TELEGRAF, data=dado_formatado)
                print(f"Enviado: {temperatura}°C | Telegraf respondeu: {resposta.status_code}")
                
            except ValueError:
                pass
            
except Exception as e:
    print(f"Erro: {e}")