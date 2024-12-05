output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}
output "identity" {
  value = azurerm_container_group.container.identity
}