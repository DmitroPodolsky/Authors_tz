# Authors_tz

## Overview

backend for authors

## Prerequisites

- **Required**: Python 3.x
- **For pip method**: pip
- **For poetry method**: poetry
- **For Docker method**: Docker

## Installation & Usage

#### Step 1: Clone the repository
Execute the following command:
```
git clone https://github.com/DmitroPodolsky/Authors_tz.git
```

#### Step 2: Navigate to the project directory
Execute the following command:
```
cd auto_ria_parser
```

#### Step 3: configure .env from .env.local or .env.docker

### Method 1: Using pip

#### Step 1: Install required packages
Execute the following command:
```
pip install -r requirements.txt
```

#### Step 2(Optional): create database in docker-compose-local.yml
Execute the following command:
```
docker compose -f docker-compose-local.yml up --build -d
```

#### Step 3: Run the app
Execute the following command:
```
python -m app
```

---

### Method 2: Using poetry

#### Step 1: Install the project and dependencies
Execute the following command:
```
poetry install
```

#### Step 2(Optional): create database in docker-compose-local.yml
Execute the following command:
```
docker compose -f docker-compose-local.yml up --build -d
```

#### Step 3: Run the bot
Execute the following command:
```
poetry run python -m app
```

---

### Method 3: Using Docker

#### Step 1: Build and run the Docker container
Execute the following command:
```
docker-compose up --build
```
