resource_groups_values = {
  rg1 = {
    rgname   = "aks-rg"
    location = "west us"
  }
}




aks_clusters_values = {
  cluster = {
    name               = "sammyaks"
    location           = "west us"
    rgname             = "aks-rg"
    dns_prefix         = "sammyaksdns"
    kubernetes_version = "1.34.7"
    node_count         = 1
    vm_size            = "Standard_D2s_v6"
  }
}


acrs_values = {
  acr = {
    name     = "sammyacr"
    location = "west us"
    rgname   = "aks-rg"
    sku      = "Basic"
  }
}

namespace_values = {
  todo = {
    name = "todo"
  }
}

deployment_values = {
  microtodoui = {
    name           = "microtodoui"
    namespace      = "todo"
    replicas       = 1

    image          = "nginx"

    container_port = 80
    app_label      = "microtodoui"
  }
}


service_values = {
  microtodoui = {
    name        = "microtodoui-lb-service"
    namespace   = "todo"

    app_label   = "microtodoui"

    port        = 80
    target_port = 80

    type        = "LoadBalancer"
  }
}


