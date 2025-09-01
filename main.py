# main.py

import queue
import threading
import time
from fastapi import FastAPI, Request, HTTPException, Response
from lxml import etree
import uvicorn

# Importa nosso MÓDULO SIMULADOR em vez do real
import printer_mock as printer_module

# Fila segura para comunicação entre a thread do servidor e a thread da impressora
print_queue = queue.Queue()

# --- Worker da Impressora (usando o MOCK) ---
def printer_worker():
    """
    Esta função roda em uma thread separada.
    Ela monitora a fila e "imprime" os dados usando o módulo mock.
    """
    print("[Printer Worker] Thread iniciada. Aguardando trabalhos de impressão...")
    while True:
        try:
            # Pega dados da fila (bloqueia até que um item esteja disponível)
            xml_data_to_print = print_queue.get()

            # Sinal para encerrar a thread
            if xml_data_to_print is None:
                print("[Printer Worker] Sinal de encerramento recebido. Finalizando thread.")
                break

            # 1. Tenta obter uma instância da impressora (mock)
            p = printer_module.get_printer()
            if not p:
                print("[Printer Worker] Erro: Não foi possível inicializar a impressora mock.")
                continue # Volta para o início do loop

            # 2. Simula a impressão
            # (Extraia os dados do XML como faria na versão final)
            # Exemplo simples:
            root = etree.fromstring(xml_data_to_print)
            titulo = root.findtext('.//titulo', default='N/A')
            item = root.findtext('.//item', default='N/A')
            valor = root.findtext('.//valor', default='N/A')

            p.text("--- INICIO DO CUPOM ---\n")
            p.text(f"Titulo: {titulo}\n")
            p.text(f"Item: {item}\n")
            p.text(f"Valor: R$ {valor}\n")
            p.text("--- FIM DO CUPOM ---\n")
            p.cut()
            p.close()

            print_queue.task_done()

        except etree.XMLSyntaxError:
            print("[Printer Worker] Erro: XML recebido na fila está mal formatado.")
        except Exception as e:
            print(f"[Printer Worker] Erro inesperado: {e}")

# --- Servidor FastAPI ---
app = FastAPI()

@app.post("/imprimir")
async def process_print_request(request: Request):
    content_type = request.headers.get('Content-Type')
    if not content_type or 'application/xml' not in content_type:
        raise HTTPException(
            status_code=415,
            detail="Tipo de conteúdo não suportado. Use 'application/xml'."
        )

    try:
        xml_body = await request.body()
        # Validação básica do XML antes de enfileirar
        etree.fromstring(xml_body)

        # Coloca o trabalho na fila para o worker processar
        print_queue.put(xml_body)

        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><status><codigo>1</codigo><mensagem>XML recebido e enfileirado para impressão com sucesso.</mensagem></status>',
            media_type="application/xml"
        )
    except etree.XMLSyntaxError:
        raise HTTPException(status_code=400, detail="O corpo da requisição contém um XML mal formatado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

# --- Inicialização ---
if __name__ == "__main__":
    # Inicia a thread do worker da impressora
    printer_thread = threading.Thread(target=printer_worker, daemon=True)
    printer_thread.start()

    # Inicia o servidor FastAPI/Uvicorn
    # Use port=8000 ou qualquer outra porta disponível
    print("Iniciando o servidor FastAPI na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # (Este código abaixo não será executado até o Uvicorn parar)
    print_queue.put(None) # Envia sinal de parada para a thread
    printer_thread.join()