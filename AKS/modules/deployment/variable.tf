variable "deployment_details" {

  type = map(object({
    name           = string
    namespace      = string
    replicas       = number
    image          = string
    container_port = number
    app_label      = string
  }))
}