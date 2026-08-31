# resource "azurerm_kubernetes_cluster_node_pool" "userpool" {
#   for_each = var.aksclusterdetails

#   name                  = "userpool"
#   kubernetes_cluster_id = azurerm_kubernetes_cluster.aks[each.key].id

#   vm_size    = "Standard_D2s_v3"
#   node_count = 2

#   mode       = "User"
#   os_type    = "Linux"

#   tags = {
#     Environment = "Dev"
#   }
# }