terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

resource "yandex_mdb_postgresql_cluster" "tf-psql-cluster" {
  name        = "tf-psql-cluster"
  environment = "PRESTABLE"
  network_id  = var.network

  config {
    version = 15
    resources {
      resource_preset_id = "s2.micro"
      disk_type_id       = "network-hdd"
      disk_size          = 16
    }
  }

  maintenance_window {
    type = "ANYTIME"
  }

  host {
    zone      = var.psql-zone
    subnet_id = var.subnet_psql
  }
}