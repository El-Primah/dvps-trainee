zone = "ru-central1-a"
network = "<network id>" # default network - enp9c40tiqa2fesa80th
subnet_psql = "<subnet id>" # default subnet in ru-central1-a default network
ssh_allow_ipv4 = [
  {
    name = "mxfr-ssh-access"
    ip   = "0.0.0.0/32"  # Замените на ваш IP
  },
]
