resource "azurerm_container_registry" "acr" {
  for_each = var.acrdetails

  name                = each.value.name
  location            = each.value.location
  resource_group_name = each.value.rgname
  sku                 = each.value.sku
  admin_enabled       = true
}