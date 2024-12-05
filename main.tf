# Terraform configuration
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0.2"
    }
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "1.1.1"
    }
  }
  required_version = ">= 1.1.0"
}

# Azure Provider
provider "azurerm" {
  features {}
}

# Azure DevOps Provider
provider "azuredevops" {
  org_service_url       = var.azure_devops_org_url
  personal_access_token = var.azure_devops_pat
}

data "azuredevops_project" "project" {
  name = "SUML"
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = "Poland Central"
}

# Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "myContainerRegistrySUML"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Role Assignment for ACR Pull
resource "azurerm_role_assignment" "acr_pull" {
  principal_id         = azurerm_container_group.container.identity[0].principal_id
  role_definition_name = "AcrPull"
  scope                = azurerm_container_registry.acr.id
}

# Container Instance
resource "azurerm_container_group" "container" {
  name                = "myContainerGroup"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"

  identity {
    type = "SystemAssigned"
  }

  container {
    name   = "my-app"
    image  = "${azurerm_container_registry.acr.login_server}/my-app:latest"
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  ip_address_type = "Public"
  dns_name_label  = "myappdnslabelSUML"
}

# Azure DevOps GitHub Service Connection
resource "azuredevops_serviceendpoint_github" "github" {
  project_id            = data.azuredevops_project.project.id
  service_endpoint_name = "GitHubServiceConnection"
  description           = "Connection to GitHub repository"

  auth_personal {
    personal_access_token = var.github_pat
  }
}

# Azure DevOps Build Pipeline
resource "azuredevops_build_definition" "pipeline" {
  project_id = data.azuredevops_project.project.id
  name       = "ShroomiePipeline"
  path       = "\\"

  repository {
    repo_type   = "GitHub"
    repo_id     = "s24191/shroomie"
    branch_name = "main"
    yml_path    = "azure-pipelines.yml" # Path to your YAML file
    service_connection_id = azuredevops_serviceendpoint_github.github.id
  }

  ci_trigger {
    use_yaml = true
  }
}

# Variables for the Pipeline
resource "azuredevops_variable_group" "variables" {
  project_id = data.azuredevops_project.project.id
  name       = "PipelineVariables"

  variable {
    name  = "DOCKER_REGISTRY_SERVER"
    value = azurerm_container_registry.acr.login_server
  }

  variable {
    name  = "RESOURCE_GROUP"
    value = azurerm_resource_group.rg.name
  }

  variable {
    name  = "LOCATION"
    value = azurerm_resource_group.rg.location
  }

  variable {
    name  = "CONTAINER_IMAGE_NAME"
    value = "my-app"
  }

  variable {
    name  = "CONTAINER_TAG"
    value = "latest"
  }
}