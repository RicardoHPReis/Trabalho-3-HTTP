import socket as s
import time as t
import logging as l
import threading as th
import hashlib as h
import pathlib as p
import os

NOME_DO_SERVER = ''
TAM_BUFFER = 2048
PORTA_DO_SERVER = 6000
ENDERECO_IP = (NOME_DO_SERVER, PORTA_DO_SERVER)

clientes = []
iniciar_server = False
    
logger = l.getLogger(__name__)
l.basicConfig(filename="server.log", encoding="utf-8", level=l.INFO, format="%(levelname)s - %(asctime)s: %(message)s")

# Funções padrão --------------------------------------------

def titulo():
    print("--------------------")
    print("      SERVIDOR")
    print("--------------------\n")


def mensagem_envio(cliente_socket : s.socket, endereco : tuple, mensagem : str):
    try:
        cliente_socket.send(mensagem.encode())
        logger.info(f"Destinatário: {endereco} - Enviado:  '{mensagem}'")
    except:
        logger.error(f"Cliente removido:  {endereco}")
        clientes.remove(cliente_socket)


def mensagem_recebimento(cliente_socket : s.socket, endereco : tuple):
    try:
        mensagem = cliente_socket.recv(TAM_BUFFER).decode('utf-8')
        logger.info(f"Remetente: {endereco} - Recebido: '{mensagem}'")
        return mensagem
    except:
        logger.error(f"Cliente removido:  {endereco}")
        clientes.remove(cliente_socket)


def chat_envio(cliente_socket : s.socket, endereco:tuple, mensagem : str):
    try:
        cliente_socket.send(mensagem.encode())
        logger.info(f"Destinatário: {endereco} - Chat enviado:  '{mensagem}'")
    except:
        logger.error(f"Cliente removido do chat:  {endereco}")
        clientes.remove(cliente_socket)
    

def chat_recebimento(cliente_socket : s.socket, endereco:tuple):
    try:
        mensagem = cliente_socket.recv(TAM_BUFFER).decode('utf-8')
        logger.info(f"Remetente: {endereco} - Chat recebido: '{mensagem}'")
        return mensagem
    except:
        logger.error(f"Cliente removido do chat: {endereco}")
        clientes.remove(cliente_socket)
    

def iniciar_servidor():
    inicializar = ''
    iniciar_server = False
    while inicializar == '':
        os.system('cls' if os.name == 'nt' else 'clear')
        titulo()
        inicializar = input("Deseja inicializar o servidor [S/N] ? ").lower().strip()
        match inicializar:
            case 's':
                iniciar_server = True
                logger.info("Servidor foi inicializado!")
            case 'sim':
                iniciar_server = True
                logger.info("Servidor foi inicializado!")
            case 'n':
                iniciar_server = False
                logger.info("Servidor não foi inicializado!")
            case 'não':
                iniciar_server = False
                logger.info("Servidor não foi inicializado!")
            case _:
                print('A escolha precisa estar nas opções acima!')
                logger.warning("Resposta para o servidor não foi aceita!")
                t.sleep(2)
                inicializar = ''
    return iniciar_server


def opcoes_servidor(cliente_socket:s.socket, endereco:tuple):
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print(f"{len(clientes)} cliente(s) conectado(s)...")
    
    opcao = 0
    cliente_opcao = mensagem_recebimento(cliente_socket, endereco).split("-")
    
    if cliente_opcao[0] == 'OPTION':
        opcao = int(cliente_opcao[1])
        
    match opcao:
        case 1:
            enviar_arquivo(cliente_socket, endereco)
            opcoes_servidor(cliente_socket, endereco)
        case 2:
            chat(cliente_socket, endereco)
            opcoes_servidor(cliente_socket, endereco)
        case 3:
            resposta = mensagem_recebimento(cliente_socket, endereco).split("-")
            if resposta[0] == "OK":
                logger.warning(f"Cliente desconectado: {endereco}")
                clientes.remove(cliente_socket)
                mensagem_envio(cliente_socket, endereco, 'OK-8-Desconectado')
                
                os.system('cls' if os.name == 'nt' else 'clear')
                titulo()
                print(f"{len(clientes)} cliente(s) conectado(s)...")


def retornar_nome_arquivos(cliente_socket:s.socket, endereco:tuple):
    os.system('cls' if os.name == 'nt' else 'clear')

    caminho = str(p.Path.cwd()) + '\Arquivos'
    file_paths = os.listdir(caminho)
    num_arquivos = len(file_paths)

    mensagem_envio(cliente_socket, endereco, str(num_arquivos))
    
    confirmacao_tam = mensagem_recebimento(cliente_socket, endereco).split("-")
    
    if(confirmacao_tam[0] == "ERROR"):
        logger.error("ERRO-1-Erro na requisição")
        os.system('cls' if os.name == 'nt' else 'clear')
        titulo()
        print("Erro na Requisição")
        t.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    
    elif(num_arquivos <= 0):
        logger.error("ERRO-2-Nenhum arquivo no servidor")
        os.system('cls' if os.name == 'nt' else 'clear')
        titulo()
        print("Nenhum arquivo no servidor")
        t.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        
    else:
        i = 0
        while i < num_arquivos:
            mensagem_envio(cliente_socket, endereco, file_paths[i])
            ack = mensagem_recebimento(cliente_socket, endereco).split("-")
            if (ack[1] == str(i+1)):
                i += 1
            
        while True:
            nome_arquivo = mensagem_recebimento(cliente_socket, endereco)
                
            if not os.path.exists(os.path.join("./Arquivos", nome_arquivo)):
                mensagem_envio(cliente_socket, endereco, "ERROR-3-Arquivo não encontrado!")
            else:
                mensagem_envio(cliente_socket, endereco, 'OK-1-Confirmação')
                break
        return nome_arquivo
    
    
def checksum_arquivo(nome_arquivo: str) -> str:
    checksum = h.md5()
    with open(os.path.join("./Arquivos", nome_arquivo), "rb") as file:
        while data := file.read(TAM_BUFFER):
            checksum.update(data)

    return checksum.hexdigest()
    
    
def enviar_arquivo(cliente_socket:s.socket, endereco:tuple):
    nome_arquivo: str = retornar_nome_arquivos(cliente_socket, endereco)
    num_pacotes: int = (os.path.getsize(os.path.join("./Arquivos", nome_arquivo)) // TAM_BUFFER) + 1
    num_digitos: int = len(str(num_pacotes))
    num_buffer: int = num_digitos + 1 + 16 + 1 + TAM_BUFFER
    checksum: str = checksum_arquivo(nome_arquivo)

    mensagem_envio(cliente_socket, endereco, f"OK-2-{num_pacotes}-{num_digitos}-{num_buffer}-{checksum}")
    inicio = mensagem_recebimento(cliente_socket, endereco).split("-")
    if inicio[0] != "OK":
        return

    with open(os.path.join("./Arquivos", nome_arquivo), "rb") as arquivo:
        i = 0
        while data := arquivo.read(TAM_BUFFER):
            hash_ = h.md5(data).digest()
            data_criptografada = b" ".join([f"{i:{'0'}{num_digitos}}".encode(), hash_, data])
            
            try:
                cliente_socket.send(data_criptografada)
                logger.info(f"Destinatário: {endereco} - Enviado:  'Pacote {i+1}'")
            except:
                logger.error(f"Cliente removido:  {endereco}")
                clientes.remove(cliente_socket)
                break
            
            while mensagem_recebimento(cliente_socket, endereco) == "NOK":
                try:
                    cliente_socket.send(data_criptografada)
                    logger.warning(f"Destinatário: {endereco} - Enviado novamente:  'Pacote {i+1}'")
                except:
                    logger.error(f"Cliente removido:  {endereco}")
                    clientes.remove(cliente_socket)
                    break
            i += 1
    logger.info(f"'OK-4-Todos os {num_pacotes} foram enviados!'")


def chat(cliente_socket: s.socket, endereco: tuple):
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print("CHAT SERVIDOR X CLIENTE\n\n")
    cliente_msg = ""
    servidor_msg = ""
    
    while servidor_msg.lower() != "sair":
        cliente_msg = chat_recebimento(cliente_socket, endereco)
        print(f"<{endereco}> {cliente_msg}")
        if cliente_msg.lower() == "sair":
            logger.warning(f"'OK-6-Saída do Chat pelo Cliente!'")
            break

        servidor_msg = input("<Servidor> ")
        chat_envio(cliente_socket, endereco, servidor_msg[:1024])
        if servidor_msg.lower() == "sair":
            logger.warning(f"'OK-6-Saída do Chat pelo Servidor!'")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    
    try:
        server_socket.bind(ENDERECO_IP)
        server_socket.listen()
        server_socket.settimeout(60)
    except:
        print('Não foi possível iniciar o servidor!')
        return

    iniciar_server = iniciar_servidor()
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print('Esperando resposta')

    while iniciar_server:
        cliente_socket, endereco = server_socket.accept()
        clientes.append(cliente_socket)
        
        thread = th.Thread(target=opcoes_servidor, args=(cliente_socket, endereco), daemon=True)
        thread.start()
        

if __name__ == "__main__":
    main()