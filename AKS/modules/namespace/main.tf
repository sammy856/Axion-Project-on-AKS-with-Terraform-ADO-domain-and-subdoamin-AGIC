resource "kubernetes_namespace" "namespace" {

  for_each = var.namespace_details

  metadata {
    name = each.value.name
  }
}