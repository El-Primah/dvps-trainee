zone = "ru-central1-a"
network = "enp9c40tiqa2fesa80th" # default network - enp9c40tiqa2fesa80th
subnet_psql = "e9brajjpnr1qmgo0n8p6" # default subnet in ru-central1-a default network
ssh_allow_ipv4 = [
  {
    name = "mxfr-ssh-access"
    ip   = "92.255.134.16/32"  # Замените на ваш IP
  },
]
