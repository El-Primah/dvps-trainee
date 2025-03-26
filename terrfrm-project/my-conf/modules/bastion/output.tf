output "bastion_ip" {
  value = yandex_compute_instance.bastion.network_interface.0.ip_address
}