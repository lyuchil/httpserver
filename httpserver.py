import socket
import sys
import time
import threading

errmsg = 'HTTP/1.1 404 NOT FOUND\r\n\r\n'
response10 = 'HTTP/1.0 200 OK\r\n\r\n'
response11 = 'HTTP/1.1 200 OK\r\n\r\n'


def working_for_client(client_server, client_addr, timeout_var, index):
    print(f"Thread {client_addr} created \n")
    client_server.settimeout(timeout_var)

    header_1 = ""

    try:
        HTTP_request = client_server.recv(1024).decode()
    except TimeoutError:
        header_1 = errmsg
        print(f"Thread {client_addr}: Error: socket recv timed out \n")
        response_1 = header_1.encode()
        client_server.send(response_1)
        client_server.close()
        sys.exit(1)
    except Exception:
        header_1 = errmsg
        print(f"Thread {client_addr}: Error: unexpected end of input \n")
        response_1 = header_1.encode()
        client_server.send(response_1)
        client_server.close()
        sys.exit(1)

        

    parse = HTTP_request.split(" ")
    file_name_temp = parse[1]
    file_name = file_name_temp.lstrip("/")
    parse2 = parse[2].split('\r\n')
    HTTP_version = parse2[0]

    if 'X-Additional-wait' in HTTP_request:
        custom_parse = HTTP_request.split()
        sleep_index = custom_parse.index('X-Additional-wait:')
        sleep_time = int(custom_parse[sleep_index + 1])
        print(f"Thread {client_addr}: Additional wait: {sleep_time} \n")
        time.sleep(sleep_time)

    if parse[0] != "GET":
        header_1 = errmsg
        print(f"Thread {client_addr}: Error: invalid request line \n")
        response_1 = header_1.encode()
        client_server.send(response_1)
        client_server.close()
        sys.exit(1)

    try:
        if HTTP_version == "HTTP/1.1":
            header_1 = response11
        elif HTTP_version == "HTTP/1.0":
            header_1 = response10
    except Exception:
        header_1 = errmsg
        print(f"Thread {client_addr}: Error: invalid request line \n")
        response_1 = header_1.encode()
        client_server.send(response_1)
        client_server.close()

    # trying to retrieve file
    if file_name == '':
        file_name = 'index.html'

    try:
        file = open(file_name, 'rb')
        requested_file = file.read()
        file.close()

        response_1 = header_1.encode()
        response_1 += requested_file
        client_server.send(response_1)
        print(f"Thread {client_addr}: Success: served file {file_name} \n")
        client_server.close()

    except FileNotFoundError:
        header_1 = errmsg
        print(f'Thread {client_addr}: Error: invalid path \n')
        response_1 = header_1.encode()
        client_server.send(response_1)
        client_server.close()


# ----- main ------

# local host value
host = "127.0.0.1"

# checking for command line argument specifying the port value, maximum request number, and the amount of time before timeout
if "--port" in sys.argv:
    port_val = sys.argv.index("--port")
    port = int(sys.argv[port_val + 1])
else:
    port = 8080

if "--maxrq" in sys.argv:
    rq_val = sys.argv.index("--maxrq")
    max_rq = int(sys.argv[rq_val + 1])
else:
    max_rq = 10

if "--timeout" in sys.argv:
    time_val = sys.argv.index("--timeout")
    timeout = int(sys.argv[time_val + 1])
else:
    timeout = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(max_rq)

total_threads = []

count = 0

while True:

    client_server, client_addr = server_socket.accept()

    if len(total_threads) == max_rq:
        print("Error too many connections")
        header = errmsg
        response = header.encode()
        client_server.send(response)
        client_server.close()
    else:
        count += 1
        print(f'Information: received new connection from {client_addr}, port {port}')

        t = threading.Thread(target=working_for_client,
                             args=(client_server, client_addr, timeout, count))
        t.start()
        total_threads.append(t)

        t.join()
        for threads in total_threads:
            if not threads.is_alive():
                total_threads.remove(threads)
                count -= 1


