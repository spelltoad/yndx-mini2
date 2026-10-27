# E09–E10: загрузка, звук и локальные listeners

Дата: 2026-10-27. Только чтение; никакие init-скрипты, звуковые программы или сетевые API не запускались. Конфиги quasar.cfg/launch.json целиком, логи, секреты, речь и микрофон не читались.

## E09 — локальная загрузка и ALSA

Метод: чтение `/etc/inittab`, `/etc/init.d/rcS`, `/etc/init.d/S99quasar`; `ls -ld` известных entrypoints; чтение `/proc/asound/cards`, `/proc/asound/pcm`, `/etc/asound.conf`; поиск имён Unix sockets только в /tmp и /run на глубине до 2.

Подтверждено:

- inittab запускает `/etc/init.d/rcS` как sysinit; serial respawn — `/sbin/getty_rabbit_hole`; shutdown вызывает rcK.
- rcS перебирает `/etc/init.d/S??*`. Для *.sh делает source в subshell с аргументом start; другие исполняет с start.
- S99quasar вызывает `/system/vendor/quasar/onboot.sh "$@"`, если файл исполняем.
- onboot.sh (2042 байта), run.sh (429), launch.json (2153), quasar.cfg (68663), q (2478), maind (21948960) существуют. Их содержимое на этом этапе не читалось.
- led_util, tcp_alsa_writer, quasar_client — ссылки на maind.

```text
ALSA card0: AML-AUGESOUND
00-00: TDM-B-sy6045s-hifi multicodec-0 : playback 1 : capture 1
00-01: PDM-dummy dummy-1 : capture 1
```

Маршрутизация по локальному /etc/asound.conf:

```text
pcm.!default = asym
  playback = softvol, control "Master Playback Volume"
    -> dmix_spk_plug (plug)
    -> dmix_spk (dmix)
    -> hw:0,0, channels 2, buffer_size 7680, period_size 960
  capture = multi
    a = hw:0,1, channels 8
    b = hw:0,0, channels 2
    output bindings: a.0, a.2, a.4, a.6, b.0, b.1

dmix ipc_key=1024; ipc_key_add_uid=false; ipc_perm=0666
```

Нельзя превращать 8 объявленных каналов slave a в утверждение «8 физических микрофонов»: в итоговый multi выведены четыре выбранных канала. Частота в этом файле явно не задана. Не измерялась частота hardware и не проверялась совместимость сторонней alsa-lib с этим dmix.

Unix socket paths в пределах поиска: `/tmp/wpa_ctrl_3937-2`, `/tmp/wpa_ctrl_3937-1`, `/run/chrony/chronyd.sock`, `/run/dhcpcd/unpriv.sock`, `/run/dhcpcd/sock`, `/run/wpa_supplicant/wlan0`, `/run/dbus/system_bus_socket`. Отсутствие updater.sock в этом ограниченном поиске не исключает другие/abstract IPC.

## E10 — сеть без активных проб

Метод: из `/proc/net/tcp{,6}` только local_address строк со state=0A (LISTEN); из udp{,6} только local_address. Remote endpoints, established connections, владельцы sockets и содержимое пакетов не собирались. Hex-порты преобразованы в десятичные локально на компьютере.

### TCP

| Bind | Порты |
|---|---|
| IPv4 wildcard 0.0.0.0 | 2222, 5081, 5555, 7447, 8099 |
| IPv4 loopback 127.0.0.1 | 53, 5037, 9850, 9875, 9877, 9878, 9882, 9884, 9887, 9895, 9898, 9899, 9903, 9906, 9908, 9910, 9911, 9912, 9913, 9917, 9921, 9923, 9924, 9926, 11124 |
| IPv6 wildcard :: | 1961, 2222, 47747 |
| IPv6 loopback ::1 | 53 |

### UDP binds

| Bind | Порты |
|---|---|
| IPv4 wildcard | 68, 5353, 7447, 55675, 56762 |
| IPv4 loopback | 53, 323 |
| LAN IPv4 (адрес уже известен из SSH) | 45200 |
| IPv6 wildcard | 546, 5353, 11125, 52717 |
| IPv6 loopback | 53, 323 |

Это наблюдение socket bindings на момент сбора, **не проверка доступности через firewall/роутер и не атрибуция процессов по портам**. Wildcard IPv6 не доказывает dual-stack IPv4. На 1961 и 8099 запросы не отправлялись.

## Внешние источники этого этапа

Полностью прочитаны страницы:

- https://hackalice.me/internals/architecture/
- https://hackalice.me/internals/network/
- https://hackalice.me/internals/gotchas/
- https://hackalice.me/internals/voice/
- https://hackalice.me/recipes/
- https://hackalice.me/recipes/llm/
- https://hackalice.me/recipes/airplay/
- https://raw.githubusercontent.com/skrashevich/quasar-bridge/main/README.md
- https://raw.githubusercontent.com/derangedabbot/yandex-station-2-airplay/main/docs/03-airplay.md

Все — live sources без pinned commit на этом этапе. Общая архитектура/голосовая страница описывают другую исследованную конфигурацию: например, в голосовой странице PDM обозначен hw:0,2, тогда как **у нас proc/asound показывает hw:0,1**. Нельзя копировать такой номер устройства в будущий модуль.

AirPlay-репозиторий содержит исторические и новые инструкции рядом (AirPlay 1/2, разные версии портов); это материал для анализа, не единая проверенная процедура для Мини 2. Quasar Bridge README заявляет проверку на Станции 2 с YAM 0.1.15, а у нас Мини 2 и YAM 0.1.18: совместимость ещё не установлена.
