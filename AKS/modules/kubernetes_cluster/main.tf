resource "azurerm_kubernetes_cluster" "aks" {

  for_each = var.aksclusterdetails

  name                = each.value.name
  location            = each.value.location
  resource_group_name = each.value.rgname
  dns_prefix          = each.value.dns_prefix
  kubernetes_version  = each.value.kubernetes_version

  default_node_pool {
    name       = "system"
    node_count = each.value.node_count
    vm_size    = each.value.vm_size
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Dev"
  }
}