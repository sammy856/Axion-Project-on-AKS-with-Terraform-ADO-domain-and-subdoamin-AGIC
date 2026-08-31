output "acr_id" {
  value = values(azurerm_container_registry.acr)[0].id
}