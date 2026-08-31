variable "acrdetails" {
  type = map(object({
    name     = string
    location = string
    rgname   = string
    sku      = string
  }))
}

