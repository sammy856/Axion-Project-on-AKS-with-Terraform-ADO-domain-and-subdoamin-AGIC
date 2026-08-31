variable "service_details" {

  type = map(object({
    name        = string
    namespace   = string
    app_label   = string
    port        = number
    target_port = number
    type        = string
  }))
}