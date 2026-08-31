resource "kubernetes_deployment" "deployment" {

  for_each = var.deployment_details

  metadata {
    name      = each.value.name
    namespace = each.value.namespace
  }

  spec {

    replicas = each.value.replicas

    selector {
      match_labels = {
        app = each.value.app_label
      }
    }

    template {

      metadata {
        labels = {
          app = each.value.app_label
        }
      }

      spec {

        container {

          name  = each.value.name
          image = each.value.image

          port {
            container_port = each.value.container_port
          }
        }
      }
    }
  }
}