# Локальное статическое исследование maind

Разрешено владельцем: копирование только maind на ПК, изолированные инструменты анализа. **Артефакт не запускать** ни на ПК, ни через эмулятор. Никаких изменений колонки. Проприетарный бинарник и окружение исключены из Git; публичную публикацию бинарника не предполагать.

## Артефакт

- Source: `/system/vendor/quasar/maind`, устройство Mini 2 из паспорта.
- Local: `artifacts/maind`.
- Size: 21948960 bytes.
- SHA-256 source и local: `7ff114e08d46d48394f9d794f89dc941f3b217bdcd3ff1ef46f1cd80fada6ec1`.
- ELF32 little-endian EM_ARM ET_DYN; interpreter `/lib/ld-linux-armhf.so.3`.
- Анализ: 2026-10-27, pyelftools 0.32, capstone 5.0.6 в `.venv`, установлены pip на ПК. Pip-пакеты закреплены по версиям, wheel-хеши не зафиксированы.

## Скрипты

Все читают **локальный** артефакт и не используют SSH или subprocess для запуска исследуемого ПО.

- `inspect_elf.py` — секции, экспортированные symbols и позиции целевых строк. Поиск байтов может находить suffix внутри bluetooth_*; для точных строк пользоваться find_xrefs.py.
- `find_xrefs.py` — **эвристический** линейный Thumb-проход, PC-relative literal/ADD ссылки и границы из ARM.exidx. Это не полный CFG/dataflow. Пропускает другие конструкции; literal pools могут декодироваться как инструкции. Результаты требуют ручной проверки и не являются доказательством reachability.
- `disassemble.py START:END [...]` — выбранные Thumb-диапазоны (hex VA), комментарии к некоторым PC-relative literals. Не полный symbolic execution; дамп может включать literal pools и EH-ветви.

В Git Bash на этом Windows-ПК:

```sh
research/led-mapping/.venv/Scripts/python.exe research/led-mapping/inspect_elf.py
research/led-mapping/.venv/Scripts/python.exe research/led-mapping/find_xrefs.py
research/led-mapping/.venv/Scripts/python.exe research/led-mapping/disassemble.py c6e980:c6ee90 c76e6a:c76f02
```

find_xrefs.py пишет локальный xrefs.json. Остальной stdout при необходимости сохранять **локально**, не на колонке. Локальные дампы — промежуточные, не нормативная вики; curated findings и ограничения: [E18–E20](../../docs/evidence/008-offline-led.md).

## Проверка результата

Две важные ссылки дополнительно проверены независимым вычислением адреса literal pool/PC и чтением строки по полученному VA (не только результатом сканера). Проверка выбрала данные в диапазоне, подтверждённом ARM.exidx, и сверила дизассемблированные инструкции. Цепочка физического события и реальный playback не наблюдались.
