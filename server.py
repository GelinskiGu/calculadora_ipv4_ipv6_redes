import socket
import re

LOCALHOST = "127.0.0.1"
PORT = 8080

def ip_para_int(ip):
    partes = list(map(int, ip.split('.')))
    return (partes[0]<<24) + (partes[1]<<16) + (partes[2]<<8) + partes[3]

def int_para_ip(num):
    return f"{(num>>24)&255}.{(num>>16)&255}.{(num>>8)&255}.{num&255}"

def calcular_subredes_ipv4(ip: str, mascara: str, n_subredes: int):
    ip_int = ip_para_int(ip)
    prefixo = int(mascara)
    nova_mascara = prefixo
    while 2**(nova_mascara - prefixo) < n_subredes:
        nova_mascara += 1
    ips_por_subrede = 2**(32 - nova_mascara)
    resultado = []
    for i in range(n_subredes):
        subrede_inicio = (ip_int & (~(ips_por_subrede-1))) + i*ips_por_subrede
        subrede_fim = subrede_inicio + ips_por_subrede - 1
        util_inicio = subrede_inicio + 1 if ips_por_subrede > 2 else subrede_inicio
        util_fim = subrede_fim if ips_por_subrede > 2 else subrede_fim
        resultado.append(f"{int_para_ip(subrede_inicio)}/{nova_mascara} {int_para_ip(util_inicio)} {int_para_ip(util_fim)}")
    return "\n".join(resultado)

def expand_ipv6(ip):
    if '::' not in ip:
        partes = ip.split(':')
        while len(partes) < 8:
            partes.append('0')
        return [x.zfill(4) for x in partes]
    partes = ip.split('::')
    esquerda = partes[0].split(':') if partes[0] else []
    direita = partes[1].split(':') if len(partes) > 1 and partes[1] else []
    faltando = 8 - (len(esquerda) + len(direita))
    nova = esquerda + ['0']*faltando + direita
    return [x.zfill(4) for x in nova]

def ipv6_para_ints(ip):
    partes = expand_ipv6(ip)
    return [int(x, 16) for x in partes]

def ints_para_ipv6(ints):
    return ":".join(f"{x:x}" for x in ints)

def ints_para_ipv6_simplificado(ints):
    hextets = [f"{x:x}" for x in ints]
    best_start = best_len = -1
    cur_start = cur_len = -1
    for i in range(8):
        if ints[i] == 0:
            if cur_start == -1:
                cur_start = i
                cur_len = 1
            else:
                cur_len += 1
        else:
            if cur_len > best_len:
                best_start = cur_start
                best_len = cur_len
            cur_start = -1
            cur_len = 0
    if cur_len > best_len:
        best_start = cur_start
        best_len = cur_len

    if best_len > 1:
        hextets = hextets[:best_start] + [''] + hextets[best_start+best_len:]
        if best_start == 0:
            hextets = [''] + hextets
        if best_start+best_len == 8:
            hextets = hextets + ['']
        ipv6 = ':'.join(hextets)

        while ':::' in ipv6:
            ipv6 = ipv6.replace(':::', '::')
    else:
        ipv6 = ':'.join(hextets)

    ipv6 = re.sub(r'\b0+([0-9a-fA-F]+)', r'\1', ipv6)

    if ipv6.endswith(':') and not ipv6.endswith('::'):
        ipv6 += ':'
    return ipv6

def calcular_subredes_ipv6(rede, mascara, n_subredes):
    mascara = int(mascara)
    n_subredes = int(n_subredes)
    nova_mascara = 56

    if nova_mascara <= mascara or nova_mascara > 64:
        return [f"Máscara inválida: não é possível gerar sub-redes /{nova_mascara} a partir de /{mascara}"]

    bits_disponiveis = nova_mascara - mascara
    max_subredes = 1 << bits_disponiveis
    if n_subredes > max_subredes:
        return [f"Não é possível criar {n_subredes} sub-redes /{nova_mascara} a partir de /{mascara}. Máximo possível: {max_subredes}"]

    base_ints = ipv6_para_ints(rede)
    resultado = []

    incremento = 0x4000

    for i in range(n_subredes):
        sub_ints = base_ints[:]
        sub_ints[3] = i * incremento
        for j in range(4, 8):
            sub_ints[j] = 0

        inicio = sub_ints[:]
        fim = sub_ints[:]
        fim[3] |= incremento - 1
        for j in range(4, 8):
            fim[j] = 0xFFFF

        subrede_str = ints_para_ipv6_simplificado(inicio)
        inicio_str = ints_para_ipv6_simplificado(inicio)
        fim_str = ints_para_ipv6_simplificado(fim)
        resultado.append(f"{subrede_str}/56 {inicio_str} - {fim_str}")

    return "\n".join(resultado)

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((LOCALHOST, PORT))
server.listen()
print("Servidor inicializado")
print("Esperando dados do cliente..")
clientConnection, clientAddress = server.accept()
print("Cliente conectado :", clientAddress)
msg = ''

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