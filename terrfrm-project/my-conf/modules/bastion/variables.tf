variable "zone" { type = string }
variable "cpu" { type = string }
variable "memory" { type = string }
variable "image_id" { type = string }
variable "disk_size" { type = string }
variable "subnet_id" { type = string }
variable "vm_user" { type = string }
variable "ssh_key_path" { type = string }
variable "sg_id" { type = list(string) }