variable "rgdetails" {
    type = map(object({
        rgname = string
        location = string
    }))
}

