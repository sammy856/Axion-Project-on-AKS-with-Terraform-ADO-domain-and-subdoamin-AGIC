variable "aksclusterdetails" {
  description = "AKS Cluster Configuration"

  type = map(object({
    name                = string
    location            = string
    rgname = string
    dns_prefix          = string
    kubernetes_version  = string
    node_count          = number
    vm_size             = string
  }))
}