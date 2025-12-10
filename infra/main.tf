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
  count       = var.admin_password == null ? 1 : 0
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

resource "azurerm_mssql_server" "server" {
  name                         = random_pet.azurerm_mssql_server_name.id
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.admin_username
  administrator_login_password = local.admin_password
  version                      = "12.0"
}

resource "azurerm_mssql_database" "db" {
  name      = var.sql_db_name
  server_id = azurerm_mssql_server.server.id

  # Cost efficiency
  sku_name = "GP_S_Gen5_1"
  auto_pause_delay_in_minutes = 60
  min_capacity = 0.5
}

resource "azurerm_container_registry" "acr" {
  name                = "${replace(var.repo_name, "/[^a-z0-9]/", "")}acr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_service_plan" "app_service_plan" {
  name                = "${var.repo_name}-asp"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  os_type             = "Linux"
  sku_name            = "F1"
}

resource "azurerm_linux_web_app" "fastapi_app" {
  name                = "cloud-api"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.app_service_plan.id

  site_config {
    linux_fx_version = "DOCKER|${azurerm_container_registry.acr.login_server}/${var.app_image_name}:latest"
  }

  app_settings = {
    "DOCKER_REGISTRY_SERVER_URL"      = azurerm_container_registry.acr.login_server
    "DOCKER_REGISTRY_SERVER_USERNAME" = azurerm_container_registry.acr.admin_username
    "DOCKER_REGISTRY_SERVER_PASSWORD" = azurerm_container_registry.acr.admin_password
    # SQL Connection Settings
    "SQL_SERVER_NAME"    = azurerm_mssql_server.server.fully_qualified_domain_name
    "SQL_DATABASE_NAME"  = azurerm_mssql_database.db.name
    "SQL_ADMIN_USER"     = azurerm_mssql_server.server.administrator_login
    "SQL_ADMIN_PASSWORD" = azurerm_mssql_server.server.administrator_login_password
  }

  identity {
    type = "SystemAssigned"
  }
}
