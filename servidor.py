import socket  # Biblioteca para comunicação via sockets
import threading  # Biblioteca para trabalhar com threads (execução simultânea)

# Dicionários para armazenar clientes conectados e seus nomes
clients, names = {}, {}
server_running = True  # Controle para o servidor estar rodando ou não

# Função para enviar mensagens a todos os clientes, exceto o remetente (opcional)
def broadcast(msg, exclude=None):
    for c in clients.values():  # Itera sobre todos os clientes conectados
        if c != exclude:  # Exclui o remetente se necessário
            try:
                c.send((msg + '\n').encode('utf-8'))  # Envia a mensagem
            except:
                pass

# Envia a lista de usuários ativos para um cliente específico ou para todos
def send_active_users(sock=None):
    active_users = ", ".join(names.keys())  # Lista de nomes ativos
    msg = f"Usuários ativos: {active_users}"  # Formata a mensagem
    if sock:  # Caso seja para um cliente específico
        sock.send((msg + '\n').encode('utf-8'))
    else:  # Caso seja para todos
        broadcast(msg)

# Função para lidar com um cliente individual
def handle_client(sock, addr):
    try:
        # Loop para solicitar um nome único ao cliente
        while True:
            name = sock.recv(1024).decode('utf-8')  # Recebe o nome
            if name in names:  # Verifica se o nome já está em uso
                sock.send("NOME_EM_USO\n".encode('utf-8'))  # Envia mensagem de erro
            else:
                sock.send("OK\n".encode('utf-8'))  # Confirmação de nome único
                break

        # Registra o cliente e adiciona seu nome
        clients[addr] = sock
        names[name] = addr
        broadcast(f"{name} entrou no chat de {addr[0]}:{addr[1]}")  # Notifica todos
        send_active_users()  # Envia a lista de usuários ativos

        # Loop para lidar com mensagens do cliente
        while True:
            msg = sock.recv(1024).decode('utf-8').strip()  # Recebe mensagem
            if msg.startswith("@"):  # Mensagem privada
                try:
                    target_name, private_msg = msg[1:].split(' ', 1)  # Divide o destinatário e a mensagem
                    if target_name == name:  # Bloqueia mensagens para si mesmo
                        sock.send("Você não pode enviar mensagens privadas para si mesmo.\n".encode('utf-8'))
                    elif target_name in names:  # Verifica se o destinatário existe
                        target_sock = clients[names[target_name]]  # Obtém o socket do destinatário
                        target_sock.send(f"{name}: {private_msg} (privado)\n".encode('utf-8'))  # Envia a mensagem privada
                    else:
                        sock.send(f"Usuário {target_name} não encontrado.\n".encode('utf-8'))  # Erro de destinatário
                except ValueError:
                    sock.send("Formato inválido. Use @nome mensagem.\n".encode('utf-8'))  # Erro de formato
            else:  # Mensagem pública
                broadcast(f"{name}: {msg}", exclude=sock)  # Envia para todos, exceto o remetente
    except:
        pass
    finally:
        # Remove o cliente ao desconectar
        if addr in clients: del clients[addr]
        if name in names: del names[name]
        broadcast(f"{name} saiu do chat.")  # Notifica todos sobre a saída
        send_active_users()  # Atualiza a lista de usuários ativos
        sock.close()  # Fecha o socket do cliente

# Função para gerenciar comandos do servidor (como encerramento)
def server_control(server):
    global server_running
    while server_running:
        command = input("Digite 'sair' para encerrar o servidor: ").strip().lower()  # Comando de entrada
        if command == "sair":  # Caso o comando seja para encerrar
            print("Encerrando o servidor...")
            broadcast("SERVIDOR_ENCERRADO")  # Notifica todos os clientes
            for c in clients.values():  # Fecha os sockets de todos os clientes
                c.close()
            server.close()  # Fecha o socket do servidor
            server_running = False  # Define que o servidor não está mais rodando
            print("Servidor encerrado com sucesso.")

# Função principal para iniciar o servidor
def start_server():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar o endereço
    server.bind(('0.0.0.0', 12345))  # Associa o socket a um endereço e porta
    server.listen()  # Habilita o socket para aceitar conexões
    print("Servidor está funcionando...")

    # Thread para gerenciar os comandos do servidor
    threading.Thread(target=server_control, args=(server,), daemon=True).start()

    # Loop principal para aceitar conexões de clientes
    while server_running:
        try:
            sock, addr = server.accept()  # Aceita uma nova conexão
            threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()  # Inicia uma thread para o cliente
        except:
            break

start_server()
