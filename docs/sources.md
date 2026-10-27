# Источники и план дальнейшей проверки

Прочитаны 2026-10-27. URL ниже — живые страницы/ветки, **не зафиксированные commit snapshots**. Факты устройства имеют приоритет при описании экземпляра; upstream нужен для интерпретации, но не заменяет диагностику. Скрипты из источников не запускались.

| ID | Источник | Использование и ограничения |
|---|---|---|
| S1 | https://hackalice.me/ | Навигация и границы применимости |
| S2 | https://hackalice.me/devices/station-mini2/ | Модель, AXG, CPU, периферия; ядро/DT/RAM/MTD согласуются с экземпляром; периферия ещё не проверена |
| S3 | https://hackalice.me/start/ssh/ | Маркеры ADB, Dropbear, схема OTA, init, reset; конкретные параметры SSH экземпляра неизвестны |
| S4 | https://hackalice.me/start/packages/ | yse, Entware, .yap, независимое окружение /opt |
| S5 | https://raw.githubusercontent.com/Marker284/yandex-station-extended/main/contrib/yandex-noupdate.sh | Исходник disable/status/restore прочитан полностью; признаки совпадают со схемой, локальная версия не сверена |
| S6 | https://hackalice.me/internals/architecture/ | Общая архитектура quasar, BusyBox init, роли maind, ALSA; страница основана на Лайте 3.21, не автоматически факт о Мини 2 |
| S7 | https://hackalice.me/recipes/yam/ | yamd, quazar-path, плагины, API, отдельное автообновление; локальная версия неизвестна |
| S8 | https://hackalice.me/devices/ | Матрица платформ и неоднозначные кодовые имена |
| S9 | https://raw.githubusercontent.com/nyakokitsu/yam/main/README.md | README сейчас UNDER CONSTRUCTION, ведёт к отдельным документам; исчерпывающей спецификацией не является |

## Связанные репозитории

- Вики и contrib: https://github.com/Marker284/yandex-station-extended
- YAM: https://github.com/nyakokitsu/yam
- Реестр yapkg: https://github.com/nyakokitsu/yapkg — обнаружен по ссылкам; содержимое ещё не изучено.
- BetterYAM: https://github.com/Yandex-Station-Universal-Repo/BetterYAM/ — альтернативный проект; **не установленная идентичность** нашего yamd, изучение пока отложено.
- apkg-источник: https://github.com/initialfox/yandex-station-repo — связан с пакетами; не считать установленным клиентом.

## Версионное уточнение второго этапа

См. [E04–E06](evidence/002-yam-provenance.md): локальный yamd совпадает с asset v0.1.18; tag разрешён в commit `34c0c82fc4db5a61ee80d9c5aba8e2670a9cecc6`. Прочитаны DEPLOYMENT.md и PACKAGES.md тега. Для дальнейшего чтения исходников использовать этот commit, не main. Обнаружены расхождения с wiki о создании автозапуска и семантике launch.mode; они записаны в свидетельствах, а не молча объединены.

Стабильная база исходников: https://github.com/nyakokitsu/yam/tree/34c0c82fc4db5a61ee80d9c5aba8e2670a9cecc6 . PLUGIN_API.md и реализация ещё не изучены.

## Дополнение по радуге

Полностью прочитан https://raw.githubusercontent.com/Marker284/yandex-station-extended/main/contrib/install-rgb-alice-mini2.sh ; payload-хеши совпадают с тремя локальными штатными паттернами, см. [E07–E08](evidence/003-modifications.md). Установщик не запускался. Это live main, commit источника пока не зафиксирован.

## LED-этап

Прочитаны https://hackalice.me/recipes/led/ и pinned [PLUGIN_API.md](https://github.com/nyakokitsu/yam/blob/34c0c82fc4db5a61ee80d9c5aba8e2670a9cecc6/docs/PLUGIN_API.md). Локальные onboot/run/q прочитаны с разрешения; LED/input исследованы только пассивными метаданными. См. [E11–E13](evidence/005-led.md), [LED](led.md). Event-to-pattern mapping для центра панели пока не установлен. Последующее уточнение: касание возобновляет музыку; основной кандидат player_continue.led, см. [E14–E15](evidence/006-playback-led.md). Узкая локальная выборка конфигурации/строк разрешена и выполнена, но не заменила runtime-доказательство. API docs не заменяют аудит LED ownership в реализации.

## Офлайн-исследование локального бинарника

[E18–E20](evidence/008-offline-led.md) — новый первичный источник: проверенная копия maind SHA-256 `7ff114e08d46d48394f9d794f89dc941f3b217bdcd3ff1ef46f1cd80fada6ec1`. Статически найден выбор player_pause/player_continue в buttons_actions.cpp/handlePlayPause. Метод, инструменты и ограничения — [research README](../research/led-mapping/README.md). Это не исходный код Яндекса и не runtime trace; эвристические xrefs вручную проверены для двух выбранных адресов.

## Приоритетная очередь (исторический план, сверять с этапами ниже)

1. YAM идентифицирован как v0.1.18; DEPLOYMENT.md/PACKAGES.md прочитаны. Далее PLUGIN_API.md и реализация безопасных API в commit `34c0c82fc4db5a61ee80d9c5aba8e2670a9cecc6`.
2. Локальные yse, S99yam и S99zdropbear прочитаны с разрешения; версии yse/Dropbear установлены по встроенным строкам. Далее при необходимости сопоставить с pinned upstream и проверить происхождение сборок. OTA-скрипт локально ещё не прочитан полностью.
3. Изучить launch/init и архитектуру конкретной сборки quasar; отдельно ограничения закрытого исходного кода.
4. Сеть https://hackalice.me/internals/network/ прочитана на архитектурном этапе; https://hackalice.me/start/recovery/ пока только обнаружена.
5. Описать проверенные интерфейсы с preconditions, read-only/mutating, permissions, inputs/outputs, privacy, failure modes, verification и rollback для изменений.

## Архитектурный этап

Полностью прочитаны architecture/network/gotchas/voice и рецепты LLM/AirPlay; связанные README Quasar Bridge и docs/03-airplay.md проекта derangedabbot. Точные URL, наблюдения и расхождения — [E09–E10](evidence/004-architecture.md). Эти источники пока live main/страницы, без commit pinning. Интерпретация — [архитектура](architecture.md); возможная декомпозиция — [proposal](extension-model.md).

Следующее чтение зависит от выбранного направления: локальные onboot/run/launch с согласованием; YAM PLUGIN_API и implementation в уже определённом commit; либо pinned guide/design/validation Quasar Bridge и исходники audio integration. Не считать обзорный README подтверждением Mini 2.

Полный обход сайта сейчас намеренно не выполнен: сначала получен паспорт, как потребовал владелец. Общие рецепты и инструкции для других моделей не копируются в рабочие процедуры без проверки применимости. Функции, описанные сайтом, не считаются доступными на устройстве до подтверждения.
