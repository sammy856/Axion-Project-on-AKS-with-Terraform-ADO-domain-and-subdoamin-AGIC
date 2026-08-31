resource "kubernetes_service" "service" {

  for_each = var.service_details

  metadata {
    name      = each.value.name
    namespace = each.value.namespace
  }

  spec {

    selector = {
      app = each.value.app_label
    }

    port {
      port        = each.value.port
      target_port = each.value.target_port
    }

    type = each.value.type
  }
}