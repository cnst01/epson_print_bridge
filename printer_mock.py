# printer_mock.py

import datetime

class MockPrinter:
    """
    Uma classe que simula uma impressora ESC/POS.
    Em vez de imprimir em hardware, ela exibe a saída no console.
    """
    def __init__(self, *args, **kwargs):
        # O construtor aceita quaisquer argumentos para ser compatível
        # com a chamada da impressora real, mas não os utiliza.
        print("=" * 40)
        print(f"[{datetime.datetime.now()}] MOCK PRINTER INITIALIZED")
        print("=" * 40)

    def text(self, content):
        """Simula a impressão de uma linha de texto."""
        # Remove a quebra de linha no final, pois o print já adiciona uma.
        clean_content = content.strip('\n')
        print(f"[PRINTING] {clean_content}")

    def cut(self, mode='PART'):
        """Simula o corte do papel."""
        print(f"---< CUT PAPER (Mode: {mode}) >---")

    def image(self, img_source):
        """Simula a impressão de uma imagem."""
        print(f"[PRINTING IMAGE] Source: {img_source}")

    def qr(self, content, *args, **kwargs):
        """Simula a impressão de um QR Code."""
        print(f"[PRINTING QR CODE] Content: {content}")

    def close(self):
        """Simula o fechamento da conexão com a impressora."""
        print("=" * 40)
        print(f"[{datetime.datetime.now()}] MOCK PRINTER CONNECTION CLOSED")
        print("=" * 40)
        print("\n") # Adiciona um espaço para o próximo cupom

def get_printer():
    """
    Função de fábrica que retorna uma instância da nossa impressora simulada.
    Isso nos permite ter uma única forma de obter a "impressora", seja ela real ou mock.
    """
    try:
        # Em um cenário real, aqui você poderia ter uma lógica para decidir
        # se retorna a impressora real ou a mock, com base em um arquivo de configuração.
        print(">>> get_printer: Returning MOCK printer instance.")
        return MockPrinter(idVendor=0x0000, idProduct=0x0000) # Args são ignorados
    except Exception as e:
        print(f"[ERROR] Could not initialize mock printer: {e}")
        return None