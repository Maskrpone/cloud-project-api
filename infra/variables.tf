variable "github_token" {
  description = "GitHub Personal Access Token"
  type        = string
  sensitive   = true # Hides value in CLI output
}

variable "repo_name" {
  description = "The name of the repository"
  type        = string
  default     = "cloud-project"
}

variable "resource_group_location" {
  type        = string
  description = "Location for all resources"
  default     = "uksouth"
}

variable "resource_group_name_prefix" {
  type        = string
  description = "Prefix of the resource group name that will be combined with a random ID so that the name be unique in the azure subscription"
  default     = "cloud"
}

variable "sql_db_name" {
  type        = string
  description = "Name of the SQL db"
  default     = "cloud-project-db"
}

variable "admin_username" {
  type        = string
  description = "Admin username"
  default     = "azureadmin"
}

variable "admin_password" {
  type        = string
  description = "Admin password of the SQL logical DB"
  sensitive   = true
  default     = null
}

variable "app_image_name" {
  type        = string
  description = "Name of the app container"
  default     = "api-container"
}

variable "streamlit_repo_name" {
  type = string
  description = "name of the streamlit repo"
  default = "cloud-streamlit"
}

variable "streamlit_app_image_name" {
  type = string
  description = "name of the streamlit image"
  default = "cloud-streamlit"
}
