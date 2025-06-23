import socket

SERVER = "127.0.0.1"
PORT = 8080

#cria o socket
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#conecta no servidor
client.connect((SERVER, PORT))

# envia credenciais
inp = input("Insira suas credenciais no formato: usuario senha\n")
client.send(inp.encode())
if inp == "exit":
    client.close()
    exit()

while True:
    # pede dados de sub-redes
    inp = input("Digite o problema a ser calculado no formato: IPv4/IPv6 ip máscara número_sub_redes_de_saida\n")
    client.send(inp.encode())
    if inp == "exit":
        client.close()
        exit()

    # recebe a resposta do servidor
    answer = client.recv(4096)
    print("Resposta é: "+answer.decode())
    print("Digite 'exit' para sair")