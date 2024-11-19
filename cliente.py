import socket, threading, tkinter as tk  # Importa bibliotecas para sockets, threads e GUI (Tkinter)
from tkinter import simpledialog, messagebox  # Importa widgets adicionais para entrada de dados e exibição de mensagens

# Função para receber mensagens do servidor
def receive_messages():
    try:
        while True:
            msg = client.recv(1024).decode('utf-8').strip()  # Recebe mensagens do servidor, decodifica e remove espaços extras
            if msg == "SERVIDOR_ENCERRADO":  # Verifica se o servidor enviou um comando de encerramento
                messagebox.showinfo("Desconectado", "O servidor foi encerrado. O chat será fechado.")  # Exibe aviso de desconexão
                root.destroy()  # Fecha a janela principal do chat
                break  # Encerra o loop de recebimento
            chat.config(state=tk.NORMAL)  # Permite edição no campo de chat para inserir a nova mensagem
            chat.insert(tk.END, msg + '\n')  # Adiciona a mensagem recebida ao final do chat
            chat.config(state=tk.DISABLED)  # Desabilita a edição novamente para evitar alterações manuais
    except:  # Caso ocorra algum erro
        client.close()  # Fecha a conexão com o servidor

# Função para enviar mensagens para o servidor
def send_message(event=None):  # O argumento 'event' permite que a função seja vinculada a eventos, como pressionar Enter
    msg = entry.get().strip()  # Obtém o texto do campo de entrada e remove espaços em branco
    if msg:  # Verifica se a mensagem não está vazia
        if msg.startswith("@"):  # Verifica se é uma mensagem privada (inicia com '@')
            try:
                target_name, private_msg = msg[1:].split(' ', 1)  # Divide o destinatário e o conteúdo da mensagem
                if target_name == username:  # Verifica se o usuário está tentando enviar mensagem para si mesmo
                    chat.config(state=tk.NORMAL)
                    chat.insert(tk.END, "Você não pode enviar mensagens privadas para si mesmo.\n")  # Exibe erro no chat
                    chat.config(state=tk.DISABLED)
                else:  # Caso o destinatário seja válido
                    client.send(msg.encode('utf-8'))  # Envia a mensagem ao servidor
                    chat.config(state=tk.NORMAL)
                    chat.insert(tk.END, f"Você: {private_msg} (privado para {target_name})\n")  # Exibe no chat local
                    chat.config(state=tk.DISABLED)
            except ValueError:  # Caso o formato da mensagem seja inválido
                chat.config(state=tk.NORMAL)
                chat.insert(tk.END, "Formato inválido. Use @nome mensagem.\n")  # Exibe erro no chat local
                chat.config(state=tk.DISABLED)
        else:  # Caso seja uma mensagem pública
            client.send(msg.encode('utf-8'))  # Envia a mensagem ao servidor
            chat.config(state=tk.NORMAL)
            chat.insert(tk.END, f"Você: {msg}\n")  # Exibe a mensagem enviada no chat local
            chat.config(state=tk.DISABLED)
        entry.delete(0, tk.END)  # Limpa o campo de entrada após enviar a mensagem

# Função para sair do chat
def exit_chat():
    client.close()  # Fecha a conexão com o servidor
    root.destroy()  # Fecha a janela principal do chat

# Função para solicitar o nome do usuário
def request_username():
    while True:
        username = simpledialog.askstring("Nome", "Digite seu nome (sem espaços ou @):")  # Exibe uma janela para entrada de nome
        if username is None:  # Verifica se o usuário clicou em "Cancelar"
            client.close()  # Fecha a conexão com o servidor
            exit()  # Encerra o programa
        if not username or ' ' in username or '@' in username:  # Verifica se o nome é inválido
            messagebox.showerror("Nome inválido", "O nome não pode conter espaços ou '@'.")  # Exibe uma mensagem de erro
            continue  # Pede o nome novamente
        client.send(username.encode('utf-8'))  # Envia o nome ao servidor
        response = client.recv(1024).decode('utf-8').strip()  # Recebe a resposta do servidor
        if response == "OK":  # Verifica se o nome foi aceito
            return username  # Retorna o nome
        else:  # Caso o nome já esteja em uso
            messagebox.showerror("Nome em uso", "Esse nome já está em uso. Tente outro.")  # Exibe uma mensagem de erro

# Bloco principal para conexão e inicialização do chat
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket para comunicação via TCP
    client.connect(('192.168.1.12', 12345))  # Conecta ao servidor no IP e porta especificados
    username = request_username()  # Solicita o nome do usuário
    root = tk.Tk()  # Cria a janela principal do chat
    root.title(f"Chat de {username}")  # Define o título da janela como "Chat de <nome do usuário>"
    chat = tk.Text(root, state=tk.DISABLED)  # Cria um campo de texto desabilitado para exibir o chat
    chat.pack()  # Adiciona o campo de texto à janela
    entry = tk.Entry(root)  # Cria um campo de entrada para digitar mensagens
    entry.pack()  # Adiciona o campo de entrada à janela
    entry.bind("<Return>", send_message)  # Vincula a tecla Enter à função de envio de mensagens
    tk.Button(root, text="Enviar", command=send_message).pack()  # Cria um botão para enviar mensagens
    tk.Button(root, text="Sair", command=exit_chat).pack()  # Cria um botão para sair do chat
    threading.Thread(target=receive_messages, daemon=True).start()  # Inicia uma thread para receber mensagens do servidor
    root.mainloop()  # Inicia o loop principal da interface gráfica
except Exception as e:  # Caso ocorra um erro
    messagebox.showerror("Erro de conexão", "Servidor indisponível ou entrada inválida.")  # Exibe uma mensagem de erro
eae
