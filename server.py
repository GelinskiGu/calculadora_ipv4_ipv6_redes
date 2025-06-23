import socket

LOCALHOST = "127.0.0.1"
PORT = 8080

def calcular_subredes_ipv4(ip: str, mascara: str, n_subredes: int):
    """
    Calcula sub-redes IPv4.
    Retorna lista de tuplas: (subrede/máscara, endereço útil inicial, endereço útil final)
    """
    pass 

def calcular_subredes_ipv6(ip: str, mascara: str, n_subredes: int):
    """
    Calcula sub-redes IPv6.
    Retorna lista de tuplas: (subrede/máscara, endereço útil inicial, endereço útil final)
    """
    pass

# cria socket no IP e porta e fica escutando
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((LOCALHOST, PORT))
server.listen()
print("Servidor inicializado")
print("Esperando dados do cliente..")
#aceita conexão do cliente
clientConnection, clientAddress = server.accept()
print("Cliente conectado :", clientAddress)
msg = ''

# recebe credenciais
data = clientConnection.recv(1024)
credenciais = data.decode().split()
if len(credenciais) != 2 or credenciais[0] != "admin" or credenciais[1] != "1234":
    print("Credenciais inválidas. Fechando conexão.")
    clientConnection.close()
    server.close()
    exit()

print("Usuário autenticado com sucesso.")

while True:
    try:
        # recebe dados de sub-redes
        data = clientConnection.recv(1024)
        if not data:
            break
        entrada = data.decode().split()
        if len(entrada) != 4:
            clientConnection.send("Entrada inválida".encode())
            continue
        tipo, ip, mascara, n_subredes = entrada
        if tipo.lower() == "ipv4":
            resultado = calcular_subredes_ipv4(ip, mascara, int(n_subredes))
        elif tipo.lower() == "ipv6":
            resultado = calcular_subredes_ipv6(ip, mascara, int(n_subredes))
        else:
            resultado = "Tipo inválido"

        clientConnection.send(str(resultado).encode())

    except Exception as e:
        print(f"Conexão encerrada ou erro: {e}")
        break

clientConnection.close()