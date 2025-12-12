terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# get the subscription
data "azurerm_subscription" "current" {}

# Random pet is used to get a random name for some resources (rg, mssql_server)
resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "azurerm_resource_group" "rg" {
  name     = random_pet.rg_name.id
  location = var.resource_group_location
}

resource "random_pet" "azurerm_mssql_server_name" {
  prefix = "cloud"
}

resource "random_password" "admin_password" {
  count       = var.admin_password == null ? 1 : 0 # After init, need to pass on the password in an env TF_VAR_admin_password
  length      = 20
  special     = true
  min_numeric = 1
  min_upper   = 1
  min_lower   = 1
  min_special = 1
}

locals {
  admin_password = try(random_password.admin_password[0].result, var.admin_password)
}

# Creation of the mssql server
resource "azurerm_mssql_server" "server" {
  name                         = random_pet.azurerm_mssql_server_name.id
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.admin_username
  administrator_login_password = local.admin_password
  version                      = "12.0"
}

# Creation of the mssql db
resource "azurerm_mssql_database" "db" {
  name      = var.sql_db_name
  server_id = azurerm_mssql_server.server.id

  # Cost efficiency
  sku_name                    = "GP_S_Gen5_1"
  auto_pause_delay_in_minutes = 60
  min_capacity                = 0.5
}

# Creation of the Azure Container Registry (to store private container images)
resource "azurerm_container_registry" "acr" {
  name                = "${replace(var.repo_name, "/[^a-z0-9]/", "")}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku           = "Basic"
  admin_enabled = true
}

# Firewall configuration to allow all Azure services to communicate 
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_log_analytics_workspace" "log_workspace" {
  name                = "${random_pet.rg_name.id}-log"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
}

resource "azurerm_container_app_environment" "env" {
  name                       = "${random_pet.rg_name.id}-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log_workspace.id
}

# Needs to create it AFTER having an image registered in the ACR
resource "azurerm_container_app" "api_app" {
  name                         = "${var.repo_name}-container"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  # Enable System-Assigned Identity to authenticate to ACR
  identity {
    type = "SystemAssigned"
  }

  # Ingress configuration to expose API publicly
  ingress {
    external_enabled = true
    target_port      = 80
    transport        = "auto"

    # TODO : Configure CORS for API
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  # Password to DB
  secret {
    name  = "sql-admin-password" # Name referenced in the 'env' block
    value = local.admin_password # password 
  }

  # Password to private ACR
  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  # Access to ACR
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  template {
    # Container Definition
    container {
      name = "api-container"
      # Full path to ACR
      image  = "${azurerm_container_registry.acr.login_server}/${var.app_image_name}:latest"
      cpu    = 0.5
      memory = "1.0Gi"

      # Environment Variables 
      env {
        name  = "SQL_SERVER_NAME"
        value = azurerm_mssql_server.server.fully_qualified_domain_name
      }
      env {
        name  = "ADMIN_USERNAME"
        value = azurerm_mssql_server.server.administrator_login
      }
      env {
        name        = "ADMIN_PASSWORD"
        secret_name = "sql-admin-password"
      }
    }
  }
}

resource "azurerm_container_app" "streamlit_app" {
  name                         = "${var.streamlit_repo_name}-container"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  ingress {
    external_enabled = true
    target_port      = 8501 # Default port for Streamlit
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  # Access to ACR 
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password" # References secret defined in api_app
  }

  template {
    container {
      name = "streamlit-container"
      image  = "${azurerm_container_registry.acr.login_server}/${var.streamlit_app_image_name}:latest"
      cpu    = 0.5
      memory = "1.0Gi"

      # Environment Variables for the Streamlit app to call the FastAPI
      env {
        name = "API_URL"
        value = "http://${azurerm_container_app.api_app.name}"
      }
    }
  }
}

# Tried for obtaining a working CD (for Azure login with GitHub actions), 
# but it is not working.
# resource "azurerm_user_assigned_identity" "github_identity" {
#   resource_group_name = azurerm_resource_group.rg.name
#   location            = azurerm_resource_group.rg.location
#   name                = "github-actions-identity"
# }
#
# resource "azurerm_role_assignment" "github_deployer_role" {
#   scope                = data.azurerm_subscription.current.id
#   role_definition_name = "Contributor"
#   principal_id         = azurerm_user_assigned_identity.github_identity.principal_id
# }
#
# resource "azurerm_federated_identity_credential" "github_deploy_credential" {
#   name                = "github-deploy-credential"
#   resource_group_name = azurerm_resource_group.rg.name
#   parent_id           = azurerm_user_assigned_identity.github_identity.id
#   issuer              = "https://token.actions.githubusercontent.com"
#   subject             = "repo:Maskrpone/cloud-project-api:ref:refs/heads/main"
#
#   # audience = ["api://AzureADTokenExchange"]
#   audience = ["api://azureadtokenexchange"]
# }

