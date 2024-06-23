import socket as s
import time as t
import logging as l
import threading as th
import hashlib as h
import pathlib as p
import os


class HTTP_Servidor:
    def __init__(self):
        self.logger = l.getLogger(__name__)
        l.basicConfig(filename="server.log", encoding="utf-8", level=l.INFO, format="%(levelname)s - %(asctime)s: %(message)s")

        self.__NOME_DO_SERVER = '127.0.0.1'
        self.__PORTA_DO_SERVER = 8000
        self.__TAM_BUFFER = 2048
        self.__ENDERECO_IP = (self.__NOME_DO_SERVER, self.__PORTA_DO_SERVER)
        
        self.__clientes = []        

        self.__server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.__server_socket.bind(self.__ENDERECO_IP)
        self.__server_socket.settimeout(60)
        self.__server_socket.listen()
        self.logger.info(f"Socket do servidor criado na porta: {self.__ENDERECO_IP}")
        
    
    def __del__(self):
        self.logger.info(f"Socket finalizado!")
        for cliente in self.__clientes:
            self.cliente.close()
            
        self.__clientes.clear()
        self.__server_socket.close()
        os.system('cls' if os.name == 'nt' else 'clear')
    
    
    def titulo(self):
        print("--------------------")
        print("      SERVIDOR")
        print("--------------------\n")


    def mensagem_envio(self, cliente_socket : s.socket, endereco : tuple, mensagem : str):
        try:
            cliente_socket.send(mensagem.encode())
            msg = mensagem.replace("\r\n", "")
            self.logger.info(f"Destinatário: {endereco} - Enviado:  '{msg}'")
        except:
            self.logger.error(f"Cliente removido:  {endereco}")
            self.__clientes.remove(cliente_socket)


    def mensagem_recebimento(self, cliente_socket : s.socket, endereco : tuple):
        try:
            mensagem = cliente_socket.recv(self.__TAM_BUFFER).decode('utf-8')
            msg = mensagem.replace("\r\n", " ")
            self.logger.info(f"Remetente: {endereco} - Recebido: '{msg}'")
            return mensagem
        except:
            self.logger.error(f"Cliente removido:  {endereco}")
            self.__clientes.remove(cliente_socket)

    
    def iniciar_servidor(self):
        inicializar = ''
        iniciar_server = False
        while inicializar == '':
            os.system('cls' if os.name == 'nt' else 'clear')
            self.titulo()
            inicializar = input("Deseja inicializar o servidor [S/N] ? ").lower().strip()
            match inicializar:
                case 's':
                    iniciar_server = True
                    self.logger.info("Servidor foi inicializado!")
                case 'sim':
                    iniciar_server = True
                    self.logger.info("Servidor foi inicializado!")
                case 'n':
                    iniciar_server = False
                    self.logger.info("Servidor não foi inicializado!")
                case 'não':
                    iniciar_server = False
                    self.logger.info("Servidor não foi inicializado!")
                case _:
                    print('A escolha precisa estar nas opções acima!')
                    self.logger.warning("Resposta para o servidor não foi aceita!")
                    t.sleep(2)
                    inicializar = ''
        return iniciar_server


    def http_enviar_pagina(self, cliente_socket:s.socket, endereco:tuple, nome_arquivo: str):
        if nome_arquivo == "/":
            nome_arquivo = "/index.html"
        
        nome_arquivo = nome_arquivo.replace("/", "")
        num_pacotes: int = (os.path.getsize(os.path.join("./Pages", nome_arquivo)) // self.__TAM_BUFFER) + 1
        
        with open(os.path.join("./Pages", nome_arquivo), "rb") as arquivo:
            i = 0
            while data := arquivo.read(self.__TAM_BUFFER):
                try:
                    cliente_socket.send(data)
                    self.logger.info(f"Destinatário: {endereco} - Enviado: 'Pacote {nome_arquivo} {i+1}'")
                except:
                    self.logger.error(f"Cliente removido:  {endereco}")
                    self.__clientes.remove(cliente_socket)
                    break
                i += 1
        self.logger.info(f"'OK-4-Todos os {num_pacotes} do arquivo {nome_arquivo} foram enviados!'")
    
    
    def http_enviar_imagem(self, cliente_socket:s.socket, endereco:tuple, nome_imagem: str):
        nome_imagem = nome_imagem.replace("/", "")
        num_pacotes: int = (os.path.getsize(os.path.join("./Images", nome_imagem)) // self.__TAM_BUFFER) + 1
        
        with open(os.path.join("./Image", nome_imagem), "rb") as arquivo:
            i = 0
            while data := arquivo.read(self.__TAM_BUFFER):
                try:
                    cliente_socket.send(data)
                    self.logger.info(f"Destinatário: {endereco} - Enviado: 'Pacote {nome_imagem} {i+1}'")
                except:
                    self.logger.error(f"Cliente removido:  {endereco}")
                    self.__clientes.remove(cliente_socket)
                    break
                i += 1
        self.logger.info(f"'OK-4-Todos os {num_pacotes} do arquivo {nome_imagem} foram enviados!'")
        
        
    def http_servidor(self, cliente_socket:s.socket, endereco:tuple):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')

            caminho_img = str(p.Path.cwd()) + '\Images'
            image_paths = os.listdir(caminho_img)
            num_images = len(image_paths)
            
            caminho_pag = str(p.Path.cwd()) + '\Pages'
            file_paths = os.listdir(caminho_pag)
            num_arquivos = len(file_paths)
            
            requisicao_http = self.mensagem_recebimento(cliente_socket, endereco).split('\n')
            http_response = requisicao_http[0].strip().split(" ")
                      
            if http_response[0] == "":
                self.logger.error("ERRO-1-Erro na Requisição")
                os.system('cls' if os.name == 'nt' else 'clear')
                self.titulo()
                print("ERRO na Requisição")
                t.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
                self.__clientes.remove(cliente_socket)
                
            elif http_response[0] != "GET":
                self.logger.error("ERRO-2-Não foi solicitado um get")
                os.system('cls' if os.name == 'nt' else 'clear')
                self.titulo()
                print("Não foi solicitado um GET no servidor")
                t.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
                self.__clientes.remove(cliente_socket)

            elif num_arquivos <= 0 and num_images <= 0:
                self.logger.error("ERRO-3-Nenhum arquivo no servidor")
                os.system('cls' if os.name == 'nt' else 'clear')
                self.titulo()
                print("Nenhum arquivo no servidor")
                t.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
                self.__clientes.remove(cliente_socket)
                
            else:
                if http_response[1].endswith(".jpg") or http_response[1].endswith(".jpeg") or http_response[1].endswith(".png"):
                    self.mensagem_envio(cliente_socket, endereco, "HTTP/1.1 200 OK\r\n\r\n")
                    self.http_enviar_imagem(cliente_socket, endereco, http_response[1])
                else:
                    self.mensagem_envio(cliente_socket, endereco, "HTTP/1.1 200 OK\r\n\r\n")
                    self.http_enviar_pagina(cliente_socket, endereco, http_response[1])
                
        except TimeoutError:
            self.mensagem_envio(cliente_socket, endereco, "HTTP/1.1 504 Gateway Timeout\r\n\r\n")
            self.http_enviar_pagina(cliente_socket, endereco, "/erro_timeout.html")
            cliente_socket.close()
        except Exception as e:
            self.mensagem_envio(cliente_socket, endereco, "HTTP/1.1 404 Not Found\r\n\r\n")
            self.http_enviar_pagina(cliente_socket, endereco, "/erro_404.html")
            cliente_socket.close()
            

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        iniciar_server = self.iniciar_servidor()
        os.system('cls' if os.name == 'nt' else 'clear')
        
        while iniciar_server:
            cliente_socket, endereco = self.__server_socket.accept()
            self.__clientes.append(cliente_socket)
            
            thread = th.Thread(target=self.http_servidor, args=(cliente_socket, endereco), daemon=True)
            thread.start()


if __name__ == "__main__":
    server = HTTP_Servidor()
    server.run()