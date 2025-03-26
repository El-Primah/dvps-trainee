variable "network" { type = string }

variable "ssh_allow_ipv4" {  # Добавляем новую переменную
  type = list(object({
    name = string
    ip   = string
  }))
  default = []
}

terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

resource "yandex_vpc_security_group" "nat-private-sg" {
  name       = "nat-private-sg"
  network_id = var.network

  egress {
    protocol       = "ANY"
    description    = "any"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  # Динамически генерируем правила для SSH
  dynamic "ingress" {
    for_each = var.ssh_allow_ipv4
    content {
      protocol       = "TCP"
      description    = ingress.value.name
      v4_cidr_blocks = [ingress.value.ip]
      port           = 22
    }
  }

  ingress {
    protocol       = "TCP"
    description    = "ext-http"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = 80
  }

  ingress {
    protocol       = "TCP"
    description    = "ext-https"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = 443
  }
}