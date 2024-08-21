# **TESODEV Order Application**
The microservices repository for the TESODEV Order Application Project
> Ubuntu 22.04

> [Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)


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