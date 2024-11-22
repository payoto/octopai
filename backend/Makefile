USERNAME = DOCKERHUB_USERNAME
REPO = DOCKERHUB_REPO

# Colors for output
GREEN = \033[0;32m
GRAY = \033[0;30m
NC = \033[0m
RED = \033[0;31m

## Setup and Configuration Commands
# Add environment name variable at the top
CONDA_ENV_NAME = octopai_env

# Check Python version
update_upgrade_ubuntu:
	@echo "$(GRAY)update && upgrade Ubuntu$(NC)"
	sudo apt update && sudo apt upgrade
	@echo "$(GREEN)✅ System updated$(NC)"

# Create and configure conda environment
create_conda_env:
	@echo "$(GRAY)Creating conda environment $(CONDA_ENV_NAME)$(NC)"
	@if conda env list | grep -q "$(CONDA_ENV_NAME)"; then \
        echo "$(RED)❗️ Conda environment $(CONDA_ENV_NAME) already exists$(NC)"; \
	else \
        conda create -n $(CONDA_ENV_NAME) python=3.11 -y && \
        echo "$(GREEN)✅ Conda environment created$(NC)"; \
	fi

# Install dependencies
install_deps: create_conda_env
	@echo "$(GRAY)Installing required packages$(NC)"
	conda run -n $(CONDA_ENV_NAME) conda install -y -q -c conda-forge --file requirements.txt
	@echo "$(GREEN)✅ Packages installed from requirements.txt$(NC)"

# Complete project setup
setup: create_conda_env install_deps
	@echo "$(GRAY)\n--- --- --- --- ---\n$(NC)"
	@echo "$(GREEN)✅ Setup complete\n$(NC)"

# Development environment activation and run fastapi
dev:
	@echo "$(GRAY)Running FastAPI server$(NC)"; \
	fastapi dev ./app/main.py; \


## Docker Commands

# Build Docker container
build_docker:
	@echo "$(GRAY)Building Docker container$(NC)"
	sudo docker build --platform linux/amd64 -t $(USERNAME)/$(REPO):latest .
	@echo "$(GREEN)✅ Docker container builded$(NC)"

# Run Docker container locally
run_docker:
	@echo "$(GRAY)Running Docker container locally$(NC)"
	sudo docker run --rm -it --env-file .env $(USERNAME)/$(REPO):latest
	
# Push Docker container to DockerHub
push_docker:
	@echo "$(GRAY)Pushing Docker container to DockerHub$(NC)"
	docker push $(USERNAME)/$(REPO):latest
	@echo "$(GREEN)✅ Docker container pushed to DockerHub$(NC)"

## Utility Commands

# Clean temporary files and directories
clean:
	@echo "$(GRAY)Cleaning temporary files and directories$(NC)"
	rm -rf .venv .env
	@echo "$(GREEN)✅ Clean complete$(NC)"


# Main targets
.PHONY: conda_env setup build_docker run_docker push_docker clean