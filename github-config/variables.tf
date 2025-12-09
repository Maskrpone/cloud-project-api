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
