import socket
import random
from dhcp.utils import get_valid_ipv4

class Client:
    
    @staticmethod
    def _send_dhcp_discover(client_socket, server_address, TID, mac_address):
        # Include the MAC address in the message
        message = f"DHCP Discover {TID} {mac_address}".encode()
        print(f"Sending message: {message.decode()}")
        client_socket.sendto(message, server_address)
   
    @staticmethod
    def _receive_dhcp_offer(client_socket):
        response, _ = client_socket.recvfrom(1024)
        response_message = response.decode()
        print(f"Received message: {response_message}")

        if response_message.startswith("DHCP Nak"):
            print("Received DHCP Nak: No IP address available. Terminating connection.")
            return None, None  # Indicates failure to obtain an IP
        elif response_message.startswith("DHCPOffer"):
            parts = response_message.split(" ")
            return parts[1], parts[2]  # Extract the offered IP and TID
        else:
            print("Unexpected message received. Terminating connection.")
            return None, None
    @staticmethod
    def _send_dhcp_request(client_socket, server_address, offered_ip, TID, mac_address):
        request_message = f"DHCP Request {offered_ip} {TID} {mac_address}".encode()
        print(f"Sending DHCP Request for IP: {offered_ip} with TID: {TID} with MAC: {mac_address}")
        
        client_socket.sendto(request_message, server_address)

    @staticmethod
    def _receive_dhcp_ack(client_socket):
        ack_message, _ = client_socket.recvfrom(1024)
        print(f"Received message: {ack_message.decode()}")
    
    @staticmethod
    def _select_random_mac():
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        random_mac = ':'.join(map(lambda x: "%02x" % x, mac))
        predefined_mac = "18:05:03:30:11:03"
        return random_mac if random.choice([True, True, True, False]) else predefined_mac       
    

    
    @staticmethod
    def start_client():
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.bind(("0.0.0.0", 68))  # Bind to 0.0.0.0:68 (DHCP client port)
        
        server_address = (get_valid_ipv4(), 67)  # DHCP server port and broadcast address

        try:
            TID = random.randint(1, 100000)  # Generate a random transaction ID
            mac_address = Client._select_random_mac()  # Generate or choose a MAC address
            Client._send_dhcp_discover(client_socket, server_address, TID, mac_address)
            offered_ip, response_TID = Client._receive_dhcp_offer(client_socket)

            if offered_ip is None or str(TID) != response_TID:
                print("Transaction ID mismatch or no IP address obtained. Exiting.")
                return

            Client._send_dhcp_request(client_socket, server_address, offered_ip, TID, mac_address)
            Client._receive_dhcp_ack(client_socket)
        finally:
            client_socket.close()
