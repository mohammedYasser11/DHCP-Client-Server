import socket

def send_dhcp_discover(client_socket, server_address):
    message = "DHCP Discover".encode()
    print(f"Sending message: {message.decode()}")
    client_socket.sendto(message, server_address)

def receive_dhcp_offer(client_socket):
    response, _ = client_socket.recvfrom(1024)
    response_message = response.decode()
    print(f"Received message: {response_message}")

    if response_message.startswith("DHCP Nak"):
        print("Received DHCP Nak: No IP address available. Terminating connection.")
        return None  # Indicates failure to obtain an IP
    elif response_message.startswith("DHCPOffer"):
        return response_message.split(" ")[1]  # Extract the offered IP
    else:
        print("Unexpected message received. Terminating connection.")
        return None

def send_dhcp_request(client_socket, server_address, offered_ip):
    request_message = f"DHCPOffered {offered_ip}".encode()
    print(f"Sending DHCP Request for IP: {offered_ip}")
    client_socket.sendto(request_message, server_address)

def receive_dhcp_ack(client_socket):
    ack_message, _ = client_socket.recvfrom(1024)
    print(f"Received message: {ack_message.decode()}")

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("127.0.0.1", 67)  # Server IP and port (localhost for testing)

    try:
        send_dhcp_discover(client_socket, server_address)
        offered_ip = receive_dhcp_offer(client_socket)

        if offered_ip is None:
            print("No IP address obtained. Exiting.")
            return
        
        send_dhcp_request(client_socket, server_address, offered_ip)
        receive_dhcp_ack(client_socket)
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
