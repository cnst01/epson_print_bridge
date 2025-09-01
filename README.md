# Servidor de Impressão XML para Impressoras Térmicas 🖨️

Um servidor de impressão local, multiplataforma (Windows e Linux), construído em Python. A aplicação hospeda um endpoint de API RESTful para receber dados em formato `.xml` e os envia para uma impressora térmica/fiscal conectada via USB, realizando uma impressão silenciosa e sem intervenção do usuário.

O objetivo principal deste projeto é criar uma ponte robusta e confiável entre sistemas web (como PDVs, ERPs e e-commerce) e o hardware de impressão local.

## ✨ Funcionalidades Principais

-   **Servidor HTTP Local:** Utiliza FastAPI para criar um endpoint robusto e documentado.
-   **Recepção de XML:** Endpoint dedicado a receber dados via POST no formato `application/xml`.
-   **Impressão Silenciosa:** Comunica-se diretamente com a impressora via USB (usando `python-escpos`), sem a necessidade de caixas de diálogo de impressão do sistema operacional.
-   **Multiplataforma:** Projetado para ser empacotado e executado em ambientes Windows e Linux.
-   **Feedback de API:** Retorna mensagens de status claras sobre o sucesso ou falha do processo de impressão.
-   **Interface Gráfica (Opcional):** Uma simples GUI em PySide6 para visualizar logs e gerenciar o status do servidor.

## 💻 Tecnologias Utilizadas

-   **Linguagem:** Python 3.9+
-   **Framework da API:** FastAPI
-   **Comunicação com Impressora:** `python-escpos`
-   **Análise de XML:** `lxml`
-   **Interface Gráfica:** `PySide6`
-   **Empacotamento:** `PyInstaller`

## 🚀 Guia de Uso

Siga os passos abaixo para configurar e executar o servidor de impressão.

### Pré-requisitos

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

### Modo 1: Simulado (Para Desenvolvimento e Testes)

Este modo não requer uma impressora física. As saídas de impressão serão exibidas no terminal.

1.  **Verifique a Configuração:**
    Certifique-se de que o arquivo principal (`main.py`) está importando o módulo de simulação (`printer_mock`).
    ```python
    # main.py
    import printer_mock as printer_module # <-- Deve estar usando o mock
    ```

2.  **Inicie o Servidor:**
    No terminal com o ambiente virtual ativado, execute:
    ```bash
    python main.py
    ```
    Você deverá ver as mensagens de inicialização do servidor FastAPI e do worker da impressora.

3.  **Envie um Trabalho de Impressão:**
    * Crie um arquivo chamado `teste.xml` com o seguinte conteúdo:
        ```xml
        <cupom>
            <titulo>Recibo de Teste</titulo>
            <item>Cafe Expresso Simulado</item>
            <valor>8.00</valor>
        </cupom>
        ```
    * Abra **outro terminal** e envie o arquivo para a API usando `curl`:

        ```bash
        # Se você estiver no CMD, Git Bash ou Linux
        curl -X POST -H "Content-Type: application/xml" --data-binary "@teste.xml" [http://127.0.0.1:8000/imprimir](http://127.0.0.1:8000/imprimir)

        # ⚠️ Se estiver usando PowerShell no Windows, use curl.exe
        curl.exe -X POST -H "Content-Type: application/xml" --data-binary "@teste.xml" [http://127.0.0.1:8000/imprimir](http://127.0.0.1:8000/imprimir)
        ```

4.  **Verifique o Resultado:**
    No terminal onde o servidor está rodando, você verá a saída do simulador, confirmando que o XML foi recebido e processado:
    ```
    [MOCK PRINTER INITIALIZED]
    [PRINTING] --- INICIO DO CUPOM ---
    [PRINTING] Titulo: Recibo de Teste
    [PRINTING] Item: Cafe Expresso Simulado
    [PRINTING] Valor: R$ 8.00
    [PRINTING] --- FIM DO CUPOM ---
    ---< CUT PAPER (Mode: PART) >---
    [MOCK PRINTER CONNECTION CLOSED]
    ```

---

### Modo 2: Real (Com Impressora Física)

Siga estes passos para usar uma impressora USB real compatível com ESC/POS.

1.  **Identifique sua Impressora:**
    Conecte a impressora na porta USB e descubra seu `idVendor` e `idProduct`.

    * **No Linux:**
        Execute `lsusb`. A saída será algo como `... ID 04b8:0202 Seiko Epson Corp. ...`. Neste caso, `idVendor=0x04b8` e `idProduct=0x0202`.

    * **No Windows:**
        Abra o "Gerenciador de Dispositivos", encontre a impressora, clique com o botão direito > "Propriedades" > aba "Detalhes". Selecione "IDs de Hardware" na lista. Você verá algo como `USB\VID_04B8&PID_0202`.

2.  **Configure o Código:**
    Altere o arquivo `main.py` para usar a impressora real. Substitua os valores de `idVendor` e `idProduct` pelos que você encontrou.

    * **Comente** a importação do `printer_mock`.
    * **Descomente** e configure a importação e instanciação da classe `Usb` da biblioteca `escpos`.

    ```python
    # main.py

    # DE:
    # import printer_mock as printer_module

    # PARA:
    from escpos.printer import Usb

    # ... dentro da função printer_worker()

    # DE:
    # p = printer_module.get_printer()

    # PARA:
    # Substitua os IDs pelos da sua impressora!
    p = Usb(idVendor=0x04b8, idProduct=0x0202, timeout=0, in_ep=0x81, out_ep=0x01)
    ```

3.  **Configure as Permissões do SO (⚠️ Passo Crítico):**

    * **No Linux:** Por padrão, o sistema não permite que um script de usuário acesse dispositivos USB diretamente. Crie uma regra "udev" para dar permissão:
        ```bash
        # Crie o arquivo de regra
        sudo nano /etc/udev/rules.d/99-escpos.rules

        # Adicione a seguinte linha (substituindo os IDs) e salve
        SUBSYSTEM=="usb", ATTRS{idVendor}=="04b8", ATTRS{idProduct}=="0202", MODE="0666"

        # Recarregue as regras do udev
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        ```
        Pode ser necessário desconectar e reconectar a impressora.

    * **No Windows:** O driver padrão da Epson pode "bloquear" o acesso direto ao dispositivo. Se o script não encontrar a impressora, você talvez precise usar a ferramenta **Zadig** para substituir o driver do dispositivo por `libusb-win32` ou `WinUSB`. **Atenção:** Este é um procedimento avançado, faça com cuidado.

4.  **Execute e Teste:**
    * Inicie o servidor como no modo simulado: `python main.py`.
    * Envie um trabalho de impressão usando o mesmo comando `curl.exe` de antes.

5.  **Verifique o Resultado:**
    Desta vez, em vez de mensagens no terminal, um cupom físico deve ser impresso pela sua impressora. O terminal ainda mostrará logs de inicialização e possíveis erros.
