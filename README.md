# **TESODEV Order Application**
The microservices repository for the TESODEV Order Application Project
> Ubuntu 22.04

> [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)


# Project

## CI/CD Pipeline
> The CI/CD pipeline for this project is configured using GitHub Actions. The pipeline automates the testing, building, and deployment of the microservices whenever there is a code change.
![I/CD pipeline](https://github.com/user-attachments/assets/b7e0888b-451d-48fb-9880-da0db625f19f)

### 1. Unit Testing
* Upon pushing code to the repository, the GitHub Action triggers the unit tests for each service.

* The ```test_customer_service.yml``` and ```test_order_service.yml``` file contains the configuration for running these tests. It sets up the necessary environment, installs dependencies, and runs the test suite using Pytest. The unit tests can be found in each microservice's ```unit_tests.py``` file.

* **ScreenShot of Unit Test Results**
![Github Actions Unit Test Results](https://github.com/user-attachments/assets/9bc52958-f4ab-43da-becf-d357660204ba)

### 2. Building Docker Images
* After the tests pass, the pipeline moves on to build Docker images for the microservices. The images are then pushed to the GitHub Container Registry or any other specified container registry.

* The ```deploy_customer_service.yml```, ```deploy_order_service.yml``` and ```deploy_gateway.yml``` files manages this part of the process. It includes steps for building the Docker images and deploying them.

### 3. Deployment
* The deployment is fully automated, the built Docker images are deployed to the server by sending a request to the [Deployment-Webhook](https://github.com/TESODEV-Order-Application/Deployment-Webhook) that listens on port 5000 to update any changed service.

## Docker Containerization
>The project uses Docker to containerize the microservices, databases and some other services.
![Docker Contaieners shown in Portrainer](https://github.com/user-attachments/assets/250349f4-5026-49bd-b496-6c4a9ade624b)

### 1. Container Management:
* As seen in the image, each microservice (```customer-service```, ```order-service```, ```gateway```) runs in its own Docker container. Additionally, supporting services like MongoDB and RabbitMQ are also containerized.

* The containers are managed using a container management tool named portrainer, which helps in maintaining and scaling the services.

## System Schema
> The system's overall architecture is illustrated in the system schema.png image.
![System Schema](https://github.com/user-attachments/assets/cb5e9ee5-ef43-4f5d-a3fa-45015f094b06)

### 1. API Gateway:
* Acts as a single entry point for external requests. It routes the requests to the appropriate microservices (Customer Microservice, Order Microservice).

### 2. Customer Microservice:
* Handles all operations related to customers. It interacts with the main MongoDB database to store and retrieve customer data.

### 3. Order Microservice:
* Manages the order-related operations. It interacts with the main MongoDB database to store and retrieve order data and logs order actions to the audit database using RabbitMQ for message brokering.

### 4. RabbitMQ Consumer
* The RabbitMQ Consumer is responsible for processing order logs sent by the Order Microservice. It listens to the order_audit_log queue, retrieves messages, and stores the order logs in the Audit Database.
![RabbitMQ](https://github.com/user-attachments/assets/d1d009e1-3991-4215-aa66-480c544ac9ef)

### 5. RabbitMQ and MongoDB:
* RabbitMQ is used for message brokering, particularly for sending order logs to the Audit Database.

* MongoDB is used as the primary data storage solution, with separate instances for main data and audit logs.

## API Documentation and Testing using Swagger
>Each microservice in this project has an Swagger UI that provides easy documentation, exploration and testing for the API endpoints directly from their browsers.

### 1. Customer Microservice
>Swagger URL: [http://193.164.4.17:8001/docs](http://193.164.4.17:8001/docs)
![customer swagger](https://github.com/user-attachments/assets/8352886c-fa1f-4107-98cc-d5c997bddfee)

* ```GET /customer/```: Retrieves a list of all customers.
* ```POST /customer/```: Creates a new customer.
* ```PUT /customer/{customerId}```: Updates the details of an existing customer based on the provided customer ID.
* ```DELETE /customer/{customerId}```: Deletes an existing customer using the customer ID.
* ```GET /customer/{customerId}```: Retrieves a specific customer by ID.
* ```GET /customer/validate/{customerId}```: Validates if a customer exists based on the customer ID.

### 2. Order Microservice
>Swagger URL: [http://193.164.4.17:8002/docs](http://193.164.4.17:8002/docs)
![order swagger](https://github.com/user-attachments/assets/dad4c27e-a084-41db-85b1-3b1b49dad634)

* ```GET /order/```: Retrieves a list of all orders.
* ```POST /order/```: Creates a new order.
* ```PUT /order/{orderId}```: Updates an existing order based on the provided order ID.
* ```DELETE /order/{orderId}```: Deletes an existing order using the order ID.
* ```GET /order/getByCustomer/{customerId}```: Retrieves all orders placed by a specific customer using the customer ID.
* ```GET /order/getByOrder/{orderId}```: Retrieves details of a specific order by order ID.
* ```PUT /order/changeStatus/{orderId}```: Changes the status of an order.

### 3. API Gateway
>Swagger URL: [http://193.164.4.17:8080/docs](http://193.164.4.17:8080/docs)
![gateway swagger](https://github.com/user-attachments/assets/006a6bcc-db83-4f8a-94ac-8dc984804a3a)

* ```GET /{full_path}```: A generic endpoint that proxies GET requests to the appropriate microservice based on the provided full path.
* ```POST /{full_path}```: Proxies POST requests to the appropriate microservice.
* ```PUT /{full_path}```: Proxies PUT requests.
* ```DELETE /{full_path}```: Proxies DELETE requests.

# Setup

## 1.	Set Up a VPS:
* If you haven’t already, provision a VPS (Virtual Private Server) from a cloud provider (such as DigitalOcean, AWS, or Google Cloud). Install your desired operating system (e.g., Ubuntu).
* Update and Upgrade the server.
    ```
    apt update
    apt upgrade
    apt autoremove
    ```

## 2. Setting Up Docker
* Install docker
    > Youtube Guide on [Setting Up Docker](https://www.youtube.com/watch?v=cqbh-RneBlk)
    ```
    sudo apt install docker.io
    ```
* Enable docker service
    ```
    sudo systemctl enable docker

    sudo systemctl status docker

    sudo docker run hello-world
    ```

## 3. Setting Up Portrainer
* Install portrainer
    > Youtube Guide on [Setting Up Portrainer](https://www.youtube.com/watch?v=y0GGQ2F2tvs&list=LL&index=138)
    ```
    docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
    ```

## 4. Setting up the Deployment Webhook
* Important Webhook Notes
    * Chnage the pywin package in requirements.txt to this
    ```
    pywin32;sys_platform == 'win32'
    ```
    * Install flask async
    ```
    pip install flask[async]
    ```
    * Customize webhook for the project
* Generate PAT in github

* Deploy Webhook
    ```
    docker login ghcr.io -u USERNAME -p <YOUR_PAT>
    
    docker run -d -p 5000:5000  --name=webhook --restart always -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/tesodev-order-application/deployment-webhook:main
    ```
* Removing and Reinstalling Guide
    * Remove Webhook Container
    ```
    docker ps -a
    docker stop <CONTAİNER_ID>
    docker rm <CONTAİNER_ID>
    ```

     * Remove Webhook Image
    ```
    docker images
    docker rmi <IMAGE_ID> 
    ```
* Removing old PAT Guide
    * Open docker login registery and delete old logins
    ```
    sudo nano ~/.docker/config.json
    ```
    ```
    https://www.redswitches.com/blog/fix-temporary-failure-in-name-resolution/#:~:text=Resolving%20the%20Temporary%20failure%20in,can%20ensure%20seamless%20internet%20connectivity.
    ```

## 5. Setting Up MongoDB
* Deploy MongoDB
    ```
    docker run -d --name mongodb -e MONGO_INITDB_ROOT_USERNAME=<USR> -e MONGO_INITDB_ROOT_PASSWORD=<PDW> -p 27017:27017 -v mongodb:/data/db --restart always mongo:latest
    ```
* For Second Database Deployment
    ```
    docker run -d --name mongodb_2 -e MONGO_INITDB_ROOT_USERNAME=<USR> -e MONGO_INITDB_ROOT_PASSWORD=<PDW> -p 27018:27017 -v mongodb_2:/data/db --restart always mongo:latest
    ```

## 6. Setting RabbitMQ
* Deploy RabbitMQ
    ```
    docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
    ```
* Change Password
   ```
   Default username: guest
   Default password: guest
   
   Admin->guest->Update this user-><PASSWORD>->Update User
   ```