# BubbleRAN O-RAN rApp SDK

[![O-RAN Compatible](https://img.shields.io/badge/O--RAN_Compatible-v2.1-green)](https://www.o-ran.org)
[![License](https://img.shields.io/badge/License-Apache_2.0_With_SDK_Addendum-blue.svg)](LICENSE)

The **BubbleRAN rApp SDK** is a Python-based software development kit designed to simplify the development, deployment, and integration of rApps (non-real-time applications) for the O-RAN RIC within the BubbleRAN architecture.
This repository includes both the SDK framework ([BubbleRAN Software License](https://bubbleran.com/resources/files/BubbleRAN_Licence-Agreement-1.3.pdf)) and rApp ([Apache 2.0 + Addendum](https://github.com/bubbleran/rApp_sdk/blob/main/LICENSE)).

## Key Features
- 🛠️ Easy-to-use Python SDK for developing rApps and AI Agents
- 🔗 Integrates the [LangGraph](https://pypi.org/project/langgraph/) library with the [A2A SDK](https://pypi.org/project/a2a-sdk/) for building AI Agents beyond POCs (ready for production)
- 📡 Supports O-RAN R1 interface in the K8s Custom Resource Definition (CRD) format
- ⚙️ Tools to communicate with BubbleRAN orchestration services
- ☁️ Cloud-native deployment with BubbleRAN [MX-ORS](https://bubbleran.com/products/mx-ors/), [MX-PDK](https://bubbleran.com/products/mx-pdk/), and [MX-AI](https://bubbleran.com/products/mx-ai/) products

## Directory Structure

```bash

rapp_sdk/
├── LICENSE              # Apache 2.0 with SDK Addendum
├── CONTRIBUTING.md      # Contribution guidelines
├── README.md            # Revised documentation
├── docs/
├── examples/            # rApp examples and template for rApp lifecycle management (LCM) 
└── src/

```


## License Structure

| Software  | License |
| ------------- |:-------------|
| rApp SDK				    | [BubbleRAN Software License](https://bubbleran.com/resources/files/BubbleRAN_Licence-Agreement-1.3.pdf) |
| BubbleRAN rApps		  | [Apache 2.0 + Addendum](https://github.com/bubbleran/rapp_sdk/blob/main/LICENSE) |
| 3rd Party rApps			| [Apache 2.0 + Addendum](https://github.com/bubbleran/rapp_sdk/blob/main/LICENSE)  | 
| Documentation				| [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/deed.en)	Guides, specifications, and examples | 

Important: When building rApps using this SDK, your application code can use Apache 2.0 + Addendum, but must agree with the rApp SDK License.


## Installation

1. Install common dependencies in Ubuntu: (at least python3.12)

```
# Update package lists
sudo apt update
# Install prerequisites
sudo apt install -y software-properties-common build-essential libssl-dev zlib1g-dev \
  libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev \
  libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev
# Add the deadsnakes PPA (which provides newer Python versions)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
# Install Python 3.12
sudo apt install -y python3.12 python3.12-venv python3.12-distutils
```

2. Set up a virtual environment

```
cd /path/to/your/rapp-sdk
python3.12 -m venv venv
source venv/bin/activate
```

3. Install the SDK

If installing from source:

```
pip3 install .
```
Or, from PyPI:
```
pip3 install br-rapp-sdk
```

## Documentation
Visit the BubbleRAN [Developer Portal](http://bubbleran.com/docs/devops-guide/odin/Odin/Overview) and [Labs](http://bubbleran.com/docs/user-guide/rapp-training/prerequisites) for:

- API reference
- rApp -> Non RT RIC -> xApp workflows
- rApp lifecycle overview
- A1 Policy models and examples
- R1 CRD specifications
- AI Agents development
- Tutorials and examples
