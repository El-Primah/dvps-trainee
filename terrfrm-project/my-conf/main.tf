variable "zone" { type = string }
variable "network" { type = string }
variable "subnet_psql" { type = string }

variable "ssh_allow_ipv4" {
  type = list(object({
    name = string  # Название правила (например, "home-ssh")
    ip   = string  # Ваш IP в формате "x.x.x.x/32"
  }))
  default = []  # По умолчанию пустой список
}


terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}
  
provider "yandex" {
   token  =  "<yc_tonek>"
   cloud_id  = "<cloud_id>"
   folder_id = "<floder_id>"
   zone      = var.zone
}

module "private" {
  source        = "./modules/private"
  cpu           = 2
  memory        = 2
  disk_size     = 20
  image_id      = "fd8kc2n656prni2cimp5" # 24.04 ubuntu
  subnet_id     = yandex_vpc_subnet.private_subnet.id
  vm_user       = "admin"
  ssh_key_path  = "/home/mxfr/.ssh/ssh-wtht-pswrd.pub"
  zone          = var.zone
  sg_id         = [module.nat-private-sg.nat-private-sg_ip]
}

module "bastion" {
  source        = "./modules/bastion"
  cpu           = 2
  memory        = 2
  disk_size     = 20
  image_id      = "fd8l704v1313gha28lj8" # образ nat инстанса
  subnet_id     = yandex_vpc_subnet.bastion_subnet.id
  vm_user       = "admin"
  ssh_key_path  = "/home/mxfr/.ssh/ssh-wtht-pswrd.pub"
  zone          = var.zone
  sg_id         = [module.nat-private-sg.nat-private-sg_ip]
}


# ниже VPC для NAT бастион-приват

resource "yandex_vpc_subnet" "private_subnet" {
  v4_cidr_blocks  = ["192.168.0.0/24"]
  zone            = var.zone
  network_id      = var.network
  name = "private_subnet"
  route_table_id = yandex_vpc_route_table.nat-bastion-route.id
}

resource "yandex_vpc_subnet" "bastion_subnet" {
  v4_cidr_blocks  = ["10.20.30.0/24"]
  zone            = var.zone
  network_id      = var.network
  name = "bastion_subnet"
}

module "nat-private-sg" {
  source = "./modules/nat-private-sg"
  network = var.network
  ssh_allow_ipv4 = var.ssh_allow_ipv4
}

resource "yandex_vpc_route_table" "nat-bastion-route" {
  name       = "nat-bastion-route"
  network_id = var.network
  static_route {
    destination_prefix = "0.0.0.0/0"
    next_hop_address   = module.bastion.bastion_ip
  }
}


# PSQL cluster

module "tf-psql-cluster" {
  source       = "./modules/psql-cluster"
  network      = var.network
  psql-zone    = var.zone
  subnet_psql  = var.subnet_psql
}

