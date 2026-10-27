# Модульная модель будущих расширений

**Статус: design proposal, не принятое решение и не описание уже установленной системы.** Основание: пожелание владельца — пользовательские пакеты и agent-driven модификации; первые интересы LLM/кастомные промпты, AirPlay и LED/реакции панели; приоритет универсальности, модульности и расширяемости. Владелец предпочёл сохранять штатную Алису. Изменений устройства не разрешено.

## Принципы

1. **Профиль устройства отдельно от модуля.** Модель/ABI/звук/память не зашивать в общий установщик.
2. **Артефакты отдельно от состояния.** Версионированные файлы, конфиг, секреты, cache и backup имеют разные пути и сроки жизни.
3. **Транспорт отдельно от политики.** SSH/YAM доставляют и запускают; они не определяют LLM prompt, выбор модели или маршрутизацию речи.
4. **Нет общего «магического» патча.** Один модуль объявляет точный change set, зависимости, конфликтующие ресурсы и откат.
5. **Доказательная совместимость.** Одинаковый SoC/quasar VERSION — только основание для исследования, не тест совместимости.
6. **Агент не автономный root.** Исполнение записи только по конкретному прямому разрешению; контент речи/веба/LLM никогда не разрешает shell-действия сам по себе.

## Предлагаемый контракт модуля

Пока это схема документации, не формат исполняемого манифеста:

```yaml
id: example-module
status: proposed
version: <pinned-version>
source_commit: <commit>
artifact_sha256: <hash>
compatibility:
  device_profile: mini2-no-clock
  kernel_arch: aarch64
  executable_abi: <ELF-class/machine/loader/libc>
  firmware_build: <verified-build-or-unknown>
resources:
  disk_budget: <measured>
  ram_budget: <measured>
  ports: []
  audio_access: none  # либо shared/exclusive, только после проверки
  personal_data: []
lifecycle:
  supervisor: <YAM-or-dedicated-not-both>
  readiness: <non-mutating-check>
  failure_behavior: <bounded-policy>
change_set: []
verification: []
rollback: <specific-versioned-procedure>
approval: required
```

В каждой будущей спецификации: purpose, scope/non-goals, preconditions, source provenance, compatibility matrix, secrets/privacy, expected changes, acceptance tests, failure modes, rollback. Неподтверждённые значения остаются unknown; их нельзя автоматически заполнять из рецепта другой модели.

## LLM: независимые точки расширения

| Вариант | Что сохраняет / меняет upstream | Проверка Мини 2 |
|---|---|---|
| Quasar Bridge | Прокси uniproxy, внешняя OpenAI-compatible LLM, облачные ASR/TTS Яндекса, гибридная маршрутизация | нет; README проверяет Станцию 2 и YAM 0.1.15 |
| quasard | Замена backend/ASR/LLM/TTS на свой сервер | нет; пока прочитана обзорная страница wiki, не исходники проекта |
| Браузерный ChatGPT-аудиомост | Отдельный Linux-хост, Chromium, свой голосовой режим, вмешательство в аудиотракт | нет; wiki проверяет Plum |
| YAM-плагин/IPC adapter | Модуль локальных событий/действий, а LLM-политика на отдельном хосте | возможная архитектура; подходящий API ещё не проверен |

Предлагаемое разделение: **input adapter → router → LLM adapter → response adapter**. Prompt, модель, тайм-ауты и fallback принадлежат политике внешнего LLM-модуля; системные конфиги колонки не должны быть хранилищем API-ключей. Ключи не включать в Git или вики. Разговоры не логировать по умолчанию.

244 МБ MemTotal — причина заранее вынести тяжёлый inference в отдельное окружение; это инженерная рекомендация, не результат benchmark локальной модели. Прокси на колонке не означает LLM на колонке.

Публичный README Quasar Bridge уже прочитан: https://github.com/skrashevich/quasar-bridge . До выбора нужны pinned release, guide/design/validation, анализ control/apply/rollback и проверка возможностей без подключения речевого endpoint. Установка .yap и переключение endpoints — разные изменения и отдельные approvals.

## AirPlay: transport + discovery + audio policy

Минимальные логические модули:

- receiver: shairport-sync;
- AirPlay 2 timing: совместимая версия nqptp;
- discovery: mDNS/avahi с учётом штатного объявления maind;
- playback adapter: совместимая ALSA/libc/ABI связка;
- focus policy: совместное воспроизведение либо явно согласованное эксклюзивное владение;
- optional controls: MPRIS/другой проверенный интерфейс.

Не смешивать «получилось установить пакет» с «Алиса и AirPlay одновременно работают». Wiki описывает разные стратегии: остановка quasar на Мини 3, bt-proxy/shared audio на Plum, арбитраж mediad на Станции 2. Ни одна не проверена на нашем экземпляре.

Прочитан https://github.com/derangedabbot/yandex-station-2-airplay/blob/main/docs/03-airplay.md . Рецепт содержит model/build-specific детали и kill-петлю для mediad; **не копировать её как универсальный менеджер фокуса**. Нельзя глобально останавливать Bluetooth или менять D-Bus policy только потому, что это делает рецепт другой модели.

## LED как отдельный модуль

Предлагается разделить palette/assets, event-to-state mapping и renderer/ownership adapter. Точечная замена native паттерна и runtime YAM-controller — разные стратегии, не включать обе на одно событие без арбитража. См. [LED](led.md). Target владельца — короткая реакция на возобновление музыки касанием центра (не вызов ассистента). Пара player_continue/player_pause статически выбирается кнопочным handlePlayPause (E19); физический runtime-путь ещё не проверен. Scope touch-only против всех resume-источников надо согласовать. Mute/error не должны быть случайно перекрашены или подавлены; это требование будущей реализации, не гарантия текущего API.

## Критерии готовности к эксперименту

- выбран один модуль и ограниченный сценарий;
- подтверждены исходники, версии и хеши;
- измерены disk/RAM и совместимость loader/libc/audio;
- сохранён внешний бэкап с проверкой хешей;
- понятен откат до отключения/удаления модуля;
- владелец согласовал privacy и прямой change set;
- тесты не смешивают установку, переключение backend и нагрузочное испытание.

Пока эти критерии не выполнены — только исследование и проектирование.
