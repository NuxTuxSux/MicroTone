import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")

    print(f"Received {message!r} from {addr!r}")

    writer.write(data)
    await writer.drain()

    print("Close the client socket")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, "127.0.0.1", 8888)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())





#######




import asyncio

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    print(f"Send: {message!r}")
    writer.write(message.encode())

    data = await reader.read(100)
    print(f"Received: {data.decode()!r}")

    writer.close()

asyncio.run(tcp_echo_client("Hello World!"))



#########


import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(1024)
    message = data.decode()
    print(f'Received message: {message}')

    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
print('hello')

########

import asyncio

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    print(f'Send message: {message}')
    writer.write(message.encode())
    await writer.drain()

    writer.close()

asyncio.run(tcp_echo_client('Hello, World!'))


# In questo esempio, il server ascolta sull'indirizzo IP 127.0.0.1 (localhost) sulla porta 8888 e utilizza la funzione handle_echo per gestire le
# connessioni entranti. La funzione handle_echo legge i dati ricevuti dal client e li visualizza a schermo.
# Il client si connette al server su 127.0.0.1 (localhost) sulla porta 8888 e invia un messaggio "Hello, World!". Il server visualizza il messaggio ricevuto e chiude la connessione.