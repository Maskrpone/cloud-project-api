terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  token = var.github_token
}

resource "github_repository" "repo" {
  name        = var.repo_name
  description = "Cloud project"
  visibility  = "public"
  auto_init   = false
}

# Create the development branch from main
resource "github_branch" "dev" {
  repository    = github_repository.repo.name
  branch        = "dev"
  source_branch = "main"
}

# Lock main branch: Require PRs, no direct pushes
resource "github_branch_protection" "main" {
  repository_id  = github_repository.repo.node_id
  pattern        = "main"
  enforce_admins = true

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = 0
  }
}

resource "github_branch_protection" "dev" {
  repository_id = github_repository.repo.node_id
  pattern       = "dev"

  enforce_admins = true

  required_status_checks {
    strict = true 
    contexts = [
      "check_formatting_and_linting",
    ]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = 0 # Allows merge without review 
  }
}

