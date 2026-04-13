variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "UAE North"
}

variable "app_service_sku" {
  description = "App Service Plan pricing tier"
  type        = string
  default     = "F1"
}