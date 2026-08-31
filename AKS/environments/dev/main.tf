module "rgs" {
  source    = "../../modules/resource_group"
  rgdetails = var.resource_groups_values
}

module "acrs" {
  source     = "../../modules/acr"
  acrdetails = var.acrs_values
  depends_on = [module.rgs]
}

module "aks" {
  source            = "../../modules/kubernetes_cluster"
  aksclusterdetails = var.aks_clusters_values
  depends_on        = [module.rgs]
}


# resource "azurerm_role_assignment" "acr_pull" {

#   principal_id         = module.aks.kubelet_identity_object_id
#   role_definition_name = "AcrPull"
#   scope                = module.acrs.acr_id
# }

module "namespace" {
  source            = "../../modules/namespace"
  namespace_details = var.namespace_values
}

module "deployment" {
  source             = "../../modules/deployment"
  deployment_details = var.deployment_values
}

module "service" {
  source          = "../../modules/service"
  service_details = var.service_values
}
