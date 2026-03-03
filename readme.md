For this project, you will design and implement a network application using socket programming. One example application is a File Transfer Application (similar to FTP). However, you are free to choose another type of network application if you prefer.

Project Preparation Requirements
Each group member must complete the following:

Study the concepts and working principles of File Transfer Protocol (FTP).

Review and understand socket programming fundamentals (TCP/UDP, client-server architecture, ports, etc.).

Review sample socket programming code and begin designing your own application architecture.
Important Reminder
You are not limited to a file transfer application. You may choose another network-based application such as:

Chat application

Simple HTTP web server

Remote command execution tool

Multiplayer game server

Messaging system

Any other client-server based application

Please start early, divide responsibilities within your group, and ensure that every member understands both the design and implementation.



Overview (FTP)
In this assignment, you will implement (simplified) FTP server and FTP client. The client shall connect to the server and support uploading and downloading of files to/from server. 


Specifications
- The server shall be invoked as:
pythonserv.py<PORTNUMBER>
<PORT NUMBER>specifiestheport atwhichftp serveraccepts connection requests.
For example: python serv.py 1234


- The ftp client is invoked as:
cli <server machine> <server port>
<server machine> is the domain name of the server (ecs.fullerton.edu). This will be
converted into 32 bit IP address using DNS lookup. For example: python cli.py
ecs.fullerton.edu 1234


Upon connecting to the server, the client prints out ftp>, which allows the user to execute
the following commands.
ftp> get <file name> (downloads file <file name> from the server)
ftp> put <filename> (uploads file <file name> to the server)
ftp> ls(lists files on theserver)
ftp> quit (disconnects from the server and exits)


 

Phase One: Local Deployment (Basic Client-Server)
In Phase One, you will:

Develop a simple client-server socket application

Deploy and run both the client and server on your local machine

Use TCP (recommended) or UDP sockets

Demonstrate successful communication between client and server

Requirements:
Server must:

Create a socket

Bind to a port

Listen for incoming connections

Accept client connections

Send/receive data

Client must:

Connect to the server

Send requests

Receive responses

Demonstrate working communication (file transfer, chat messages, command execution, etc.)

This phase focuses on:

Understanding socket programming

Connection handling

Data transmission

Basic error handling

Phase Two: Cloud Deployment
In Phase Two, you will deploy the same application in a cloud environment.

You are encouraged to be creative in your deployment design.

Minimum Requirement:
Deploy the server on a cloud platform

Run the client from your local machine

Demonstrate successful remote communication

For example:

Deploy the server on an Amazon Web Services EC2 instance

Open the necessary port in the security group

Connect from your local client using the public IP

Advanced / Creative Options 
You may choose a more comprehensive cloud architecture, such as:

Deploying on Amazon Web Services using:

Amazon EC2

Elastic Load Balancing

Amazon S3 (for file storage)

Auto Scaling group

Containerizing your app using Docker

Deploying with Kubernetes

Using a reverse proxy

Adding authentication

Supporting multiple concurrent clients

Implementing logging and monitoring

Your cloud design can be:

Simple (single VM server)
OR

Architecturally advanced (multi-tier design)

Your creativity and architectural thinking will be considered.

Deliverables
For each phase, you must submit:

Source code (client and server)

Report: Brief technical explanation of:
Architecture diagram
Deployment step
Socket type used (TCP/UDP)

Port configuration

Cloud networking setup (Phase Two)