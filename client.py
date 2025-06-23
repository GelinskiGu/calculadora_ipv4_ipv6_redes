import socket

SERVER = "127.0.0.1"
PORT = 8080

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((SERVER, PORT))

inp = input("Insira suas credenciais no formato: usuario senha\n")
client.send(inp.encode())
if inp == "exit":
    client.close()
    exit()

while True:
    inp = input("Digite o problema a ser calculado no formato: IPv4/IPv6 ip máscara número_sub_redes_de_saida\n")
    client.send(inp.encode())
    if inp == "exit":
        client.close()
        exit()

    answer = client.recv(4096)
    print("Saídas: \n"+answer.decode())
    print("Digite 'exit' para sair")