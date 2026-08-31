output "kubelet_identity_object_id" {
  value = values(azurerm_kubernetes_cluster.aks)[0].kubelet_identity[0].object_id
}

output "host" {
  value = values(azurerm_kubernetes_cluster.aks)[0].kube_config[0].host
}

output "client_certificate" {
  value = values(azurerm_kubernetes_cluster.aks)[0].kube_config[0].client_certificate
}

output "client_key" {
  value = values(azurerm_kubernetes_cluster.aks)[0].kube_config[0].client_key
}

output "cluster_ca_certificate" {
  value = values(azurerm_kubernetes_cluster.aks)[0].kube_config[0].cluster_ca_certificate
}