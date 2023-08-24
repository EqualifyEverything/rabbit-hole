<<<<<<< HEAD

# A11yRabbit Hole
[![🏗️📤 Build and publish 🐳 images](https://github.com/EqualifyApp/rabbit-hole/actions/workflows/containerize.yml/badge.svg)](https://github.com/EqualifyApp/rabbit-hole/actions/workflows/containerize.yml)

Welcome to the A11yRabbit Hole! This repo serves as your trusty guide, helping you explore the wild world of web accessibility testing within the EqualifyApp ecosystem 🧭🕳️🐇.

## How It Works

This repo mainly focuses on processing web accessibility scans and crawling data. It listens to RabbitMQ, processes incoming messages, and updates the accessibility testing information accordingly.

## Getting Started

To hop on this adventure, consider deploying the Let's Go Stack or a Stand Alone Container.

| Env Var | Default | Options | Notes |
|-----------|-----------|-----------|-----------|
| APP_PORT     | 8084     | Any port number     | port doesn't need to be exposed if not using api endpoint     |

### Deploy the Let's Go Stack 🌐

The ecosystem can be deployed via a simple docker-compose file. Find more info on deploying the stack here: [https://github.com/EqualifyApp/lets-go](https://github.com/EqualifyApp/lets-go)

### Deploy Stand Alone Container 🐳

Get the standalone container from Docker Hub and start your own Rabbit Hole adventure.

```bash
docker pull equalifyapp/rabbit-hole:latest
docker run --name rabbit-hole -p 8084:8084 equalifyapp/rabbit-hole:latest
```

## Repo Summary
This repo takes you through the following files and directories:

- **Dockerfile**: The blueprint for building the Docker image 🏗️
- **requirements.txt**: The list of necessary python packages 📜
- **src**: The source folder containing most of the magic ✨
    - **record.py**: The main script for processing messages 🎬
    - **data**: Stores data access scripts 📂
        - **access.py**: Handles database connections for inserting and updating data 🗄️


### A File-by-File Breakdown
#### Dockerfile 🐳
Here we have a Dockerfile that defines the base Python image, sets the working directory, copies necessary files, installs dependencies, sets environment variables, and exposes the necessary port. After that, it releases the krak... uh, main.py! 😈

#### requirements.txt 📜
This little file contains a list of dependencies our rabbit hole needs to run. 🐇+📚=🏃

#### src
The mystical land of our rabbit hole. 🕳️

##### record.py 🎬
Yep, record.py is our main script that listens to various RabbitMQ queues, processes incoming messages, and calls corresponding processing functions from queue_processors.

#####  src/data
Here lie the scripts that handle all things datay. 📚

###### access.py
Welcome to the database guardian! This file specifies the connection class that takes care of opening and closing the database connections, multiplies their rabbit-ness by performing tests, and, of course, securing their whereabouts. 🐇🔐

### License
This repo is under the GPL-3.0 License. In a nutshell, this means you're free to use, modify, and distribute this software as long as you follow the requirements specified in the LICENSE file. You can find it here: [LICENSE](LICENSE)

## Happy exploring the A11yRabbit Hole! 🕳️🐇🎉

# rabbit-hole
Where the data hops in from RabbitMQ and burrows into the database, deep down the rabbit hole 🐰🕳️.

=======
# rabbit-hole
Where the data hops in from RabbitMQ and burrows into the database, deep down the rabbit hole 🐰🕳️.
>>>>>>> 11a3f75 (Initial commit)
