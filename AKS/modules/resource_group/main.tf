resource "azurerm_resource_group" "rg" {
    for_each = var.rgdetails 
    name = each.value.rgname
    location = each.value.location
}

# declare/define
# use
# avalaue assign