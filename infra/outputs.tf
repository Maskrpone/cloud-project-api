output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "sql_server_name" {
  value = azurerm_mssql_server.server.name
}

output "admin_username" {
  value = var.admin_username
}


output "admin_password" {
  sensitive = true
  value     = local.admin_password
}

output "resource_group_id" {
  description = "ID of the azure resource group"
  value       = azurerm_resource_group.rg.id
}
