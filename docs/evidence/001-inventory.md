# Свидетельства первого диагностического среза

Дата: 2026-10-27, около 08:08 UTC по компьютеру. Формат: отобранные результаты и метод; это **не полный raw transcript**. Все SSH-команды выполнялись root; только запросы чтения. Установленные скрипты и менеджеры пакетов не запускались. Отдельного архива исходных выводов пока нет.

## E01 — идентификация

Транспорт (обезличенный шаблон): `ssh -p <SSH_PORT> -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 <SSH_USER>@<SPEAKER_HOST> '<diagnostics>'`. Реальные параметры сохранены только в локальном private/device.local.md и исключены из Git. Подключение прошло с существующим known-host key; ключ не принимался автоматически.

Метод: `uname -srm`; чтение `/etc/os-release`, `/etc/issue`; `tr '\000' '\n'` для `/proc/device-tree/model` и `compatible`; фильтр CPU-полей `/proc/cpuinfo` без Serial.

```text
Linux 4.9.68 aarch64
NAME=Buildroot
VERSION=2020.02.1-ge4999fe
ID=buildroot
VERSION_ID=2020.02.1
BUILD_ID=4793643989
BUILD_TYPE=user
Yandex Station Mini 2
yandex,station-mini2
amlogic, axg
CPU implementer: 0x41
CPU architecture: 8
CPU part: 0xd03 (четыре записи)
Hardware: Amlogic
```

`command -v` нашёл `/bin/busybox`, но не yse/opkg/dpkg/rpm/apt/python3/dropbear/sshd/systemctl в PATH этой сессии. Пакет завершился кодом 127 из-за последней неудачной проверки command -v, не из-за отказа SSH. Позднее бинарники найдены по абсолютным путям.

## E02 — платформа и следы расширений

Метод: чтение VERSION, выбранных полей meminfo, `/proc/mtd`, `/proc/mounts`; `df -h / /data /opt`; листинг только выбранных каталогов расширений и `/etc/init.d`; имена процессов через `/proc/*/comm`; `od -An -tx1 -N20` трёх ELF-файлов.

```text
/system/vendor/quasar/VERSION: 3.21
MemTotal: 243996 kB
MemAvailable: 143140 kB
SwapTotal: 0 kB
/bin/busybox:                   ELF magic; class 01; data 01; machine 28 00
/system/vendor/quasar/maind:     ELF magic; class 01; data 01; machine 28 00
/data/opt/bin/dropbear:          ELF magic; class 01; data 01; machine 28 00
```

`01` ELF class = ELF32; `28 00` = EM_ARM, не AArch64. Полная MTD-карта, ключевые mount points и df перенесены в [паспорт](../device.md).

Наблюдены `/etc/init.d/S99yam`, `S99zdropbear`, `S99quasar`, `S99input-event-daemon`; имена процессов `yamd`, `dropbear`, `adbd`, `quasar_launcher`, `maind`. Полные cmdline/env не выгружались.

В `/data/opt/bin`: dropbear, dropbearkey, yse. В `/data/opt`: entware, backup, etc, home, S99zdropbear, yandex-noupdate.sh. В backup: device_ota_update.sh.orig, launch.json.orig, ota_script.pub.orig. Наличие копий не доказывает подлинность и пригодность для отката.

## E03 — уточнение модификаций

Метод: из `/opt/lib/opkg/status` только Package/Version/Architecture/Status; `readlink` ссылок и exe процесса yamd; выделение path tokens из S99yam; подсчёт строк updatesd в двух launch.json; чтение текущего applier только после проверки размера <1024 байт; sha256sum двух пар OTA-файлов; lsattr двух маркеров. Для maind из cmdline выводились только аргументы, целиком соответствующие `^--[a-z_]+$`.

```text
/data -> /bkupgrade/data
/opt -> /data/opt/entware
yamd exe: /bkupgrade/data/quazar/yam/bin/yamd
launch.json updatesd lines: 0
backup/launch.json.orig updatesd lines: 2
maind role flags observed: --telemetry, --platformd, --mediad
activate_adb_quasmodrom: -----i---c---, размер 0
activate_network_adb:   -----i---c---, размер 0
```

Наблюдаемый applier, 101 байт:

```sh
#!/bin/sh
# disabled by yandex-noupdate.sh
logger -t noupdate "OTA apply blocked" 2>/dev/null
exit 0
```

Он **прочитан, не исполнен**.

| Файл | SHA-256 |
|---|---|
| /system/vendor/quasar/ota_script.pub | 17baed47b478617fa277d4eb9db7fe23a33a3554d1bef84be46ec1fd18b46212 |
| /data/opt/backup/ota_script.pub.orig | 34149e00772820a872755c3a7a94f10c3c8ae1411c547db54168cd9a4ca65332 |
| /system/vendor/quasar/device_ota_update.sh | 3e9348acd5b4cea6ac8411596e6461ab3fd1cd4765437fc9a884f0b80bf15650 |
| /data/opt/backup/device_ota_update.sh.orig | 266efdb9b3c5ff149f5a6da2813a95f032e608f5aed3f7d90315952f3f9a0077 |

18 записей installed в Entware перечислены в паспорте. Архитектура: aarch64-3.10 либо all. YAM package database не читалась.

## Ограничения

Не читались devices.json, Wi-Fi-конфиги, ключи SSH, логи, распознанная речь, настройки/данные плагинов. Не проверялись сетевые listeners, аутентификация и firewall. Не выполнялись перезагрузка, тест OTA, API YAM или аппаратные пробы. Обычная работа демонов, включая возможные автообновления, продолжается независимо от исследования.
