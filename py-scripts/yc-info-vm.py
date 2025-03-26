import os
import grpc
import yandexcloud

from yandex.cloud.compute.v1.instance_service_pb2 import GetInstanceRequest
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.compute.v1.instance_service_pb2 import InstanceView

# Коды цветов для print

COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m" # Сброс цвета
}

def format_bytes(size):
    # Конвертация байтов в ГБ/МБ
    power = 2**30
    if size >= power:
        return f"{size / power:.1f} GB"
    else:
        return f"{size / (2**20):.1f} MB"

# для оформления вывода
def print_section(title):
    print(f"{COLORS["CYAN"]}---{title}---{COLORS['RESET']}")

def main():
    sdk = yandexcloud.SDK(token="y0_AgAEA7qkoFiZAATuwQAAAAEVHL5WAAAyYJ8u811INKSTYD2ZxqgEgWD7xw")

    print(f"{COLORS['MAGENTA']}Получение инфы об инстансе{COLORS['RESET']}")
    instanse_id = str(input(f"{COLORS['MAGENTA']}Введите id инстанса: {COLORS['RESET']}"))



    try:
        service = sdk.client(InstanceServiceStub)
        response = service.Get(
            GetInstanceRequest(
                instance_id=instanse_id,
                view = InstanceView.FULL
            )
        )
        print(f"{COLORS['GREEN']}Информация об инстансе: {COLORS['RESET']}")

        print_section("Основная информация")
        print(f"{COLORS['YELLOW']}Имя: {COLORS['RESET']}{response.name}")
        print(f"{COLORS['YELLOW']}ID: {COLORS['RESET']}{response.id}")
        print(f"{COLORS['YELLOW']}Статус: {COLORS['RESET']}{response.status}")
        print(f"{COLORS['YELLOW']}Зона доступности: {COLORS['RESET']}{response.zone_id}")
        print(f"{COLORS['YELLOW']}Тип инстанса: {COLORS['RESET']}{response.platform_id}")

        print_section("Сетевые интерфейсы")
        for i, interface in enumerate(response.network_interfaces, 1):
            print(f"\n{COLORS['YELLOW']}Интерфейс #{i}{COLORS['RESET']}")
            print(f"{COLORS['YELLOW']}Внутренний IPv4: {COLORS['RESET']}{interface.primary_v4_address.address}")
            if interface.primary_v4_address.one_to_one_nat:
                print(f"{COLORS['YELLOW']}Публичный IPv4: {COLORS['RESET']}{interface.primary_v4_address.one_to_one_nat.address}")

        print_section("Ресурсы")
        print(f"{COLORS['YELLOW']}vCPU: {COLORS['RESET']}{response.resources.cores}")
        print(f"{COLORS['YELLOW']}Память: {COLORS['RESET']}{format_bytes(response.resources.memory)}")
        print(f"{COLORS['YELLOW']}Core Fraction: {COLORS['RESET']}{response.resources.core_fraction}%")

        print_section("Диски")
        if response.boot_disk:
            boot_disk = response.boot_disk
            print(f"{COLORS['YELLOW']}Загрузочный диск:{COLORS['RESET']}")
            print(f"  ID: {boot_disk}")

        if response.secondary_disks:
            print(f"\n{COLORS['YELLOW']}Дополнительные диски:{COLORS['RESET']}")
            for i, disk in enumerate(response.secondary_disks, 1):
                print(f"  Диск #{i}: {disk.disk.id} ({format_bytes(disk.disk.size)})")

        print_section("Метаданные")
        for key, value in response.metadata.items():
            print(f"{COLORS['YELLOW']}{key}: {COLORS['RESET']}{value}")

        choice = input(f"{COLORS['YELLOW']}Вывести полную информацию? (y|n): {COLORS['RESET']}")

        while (choice != "Y" and choice != "N" and choice != "y" and choice != "n"):
            choice = input(f"{COLORS['YELLOW']}Неверный ввод.\nВывести полную информацию? (y|n): {COLORS['RESET']}\n")
        
        if (choice == "Y" or choice == "y"):
            print(response)

    except Exception as e:
        print(f"{COLORS['RED']}Ошибка при получении инфы: {COLORS['RESET']}{str(e)}")


if __name__ == "__main__":
    main()