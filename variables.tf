variable "resource_group_name" {
  default = "myTFResourceGroup"
}

variable "project_name" {
  default = "SUML"
}
variable "docker_username" {
  default = "grandtea"
}
variable "docker_password" {
  sensitive = true
}
variable "github_pat" {
  description = "Personal Access Token for GitHub"
  type        = string
  sensitive   = true
}
variable "azure_devops_pat" {
  description = "Personal Access Token for Azure DevOps"
  type        = string
  sensitive   = true
}
variable azure_devops_org_url{
  description = "Azure DevOps Organization URL for Azure DevOps"
  default = "https://dev.azure.com/SUML-YY"
}
