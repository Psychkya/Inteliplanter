import socket

localIP = "0.0.0.0"
localPort = 20001

bufferSize = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind((localIP, localPort))

print("UDP listening....")

while(True):
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	
	message = bytesAddressPair[0]
	
	address = bytesAddressPair[1]
	
	(clientIP, clientPort) = address
	
	clientMsg = "Message from client: {}".format(message)
	clientAddr = "Client IP is: {}".format(address)
	
	print(clientMsg)
	print(clientAddr)
	sendToESP = "RPI got packet"
	
	UDPServerSocket.sendto(sendToESP, address)
