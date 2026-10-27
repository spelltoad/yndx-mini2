# E16–E17: touch play/pause и предел статического поиска строк

Дата: 2026-10-27. Следующий шаг, выбранный владельцем: подтвердить mapping LED. Только статическое чтение, никаких input-событий, проигрывания паттернов или модификаций.

## E16 — наблюдение владельца

- Одинаковое касание центра переключает play/pause.
- Фиолетовая индикация появляется **и при resume, и при pause** от касания.
- Воспроизведение через голосового агента **не включает** фиолетовый индикатор.
- Желаемое направление будущего эффекта — бегущий или иной, не просто однотонная замена.

Это наблюдение источника события, не runtime trace кода. Оно не доказывает, что один и тот же .led проигрывается в обоих направлениях: визуально похожие player_continue/player_pause имеют разные кадры/тайминг (E15).

## E17 — отфильтрованные строки бинарника и скаляры config

Метод: `strings /system/vendor/quasar/maind`, regex по player_continue/player_pause, play-pause identifiers и LED pattern classes/messages, не более первых 100 совпадений. Это строки статического файла, не пользовательские логи процесса. Из quasar.cfg только safe scalar regex для заранее выбранных ключей, без вывода секций.

Наблюдены литералы:

```text
Toggle PlayPause
playback_toggle_play_pause
handleTogglePlayPause
handlePlayPause
playPauseId
playPauseBlockedByDeviceControlPanel
play_pause
player_pause
player_pause.led
player_pause.scled
player_continue
bluetooth_player_pause
bluetooth_player_continue
general_conversation_player_pause
audio_player_continue_directive
/system/vendor/quasar/ledpatterns
led_pattern_storage.cpp
sc_led_pattern.cpp
led_pattern.cpp
LedPatternStorage.NoSuchPattern
LedControllers of patterns must be the same
```

Также присутствует RTTI-имя lambda, содержащее:

```text
YandexIO::PlaybackControlCapabilityProxy::togglePlayPause(
  NAlice::TEventSource,
  YandexIO::IPlaybackControlCapability::Params const&)
```

Выше — человекочитаемая интерпретация mangled RTTI строки, не вызов demangler/отладчика и не доказательство реализации тела функции. Наличие параметра EventSource **согласуется с возможностью source-dependent обработки**, но не устанавливает конкретное сравнение touch/voice или LED dispatch.

Config scalar выборка:

```text
"press_button_play_pause" : true
"press_button_touch" : true
```

Без извлечения родительского контекста эти значения нельзя трактовать как привязку физической панели: они могут относиться к возможностям/экспериментам/другой секции. Смысл контекста пока неизвестен.

## Итог

Есть несколько независимых статических оснований для гипотезы **source-dependent media feedback**, но не прямое доказательство:

1. владелец наблюдает различие touch/voice;
2. бинарник содержит play/pause handler names и EventSource в RTTI;
3. player_continue/player_pause реально существуют и визуально согласуются с наблюдением;
4. бинарник содержит соответствующие pattern identifiers и LED storage classes.

**Mapping не подтверждён окончательно.** Strings не показывает cross-references, условия ветвлений и текущую конфигурацию. Нельзя заявлять цепочку `touch → player_continue/player_pause` установленным фактом.

## Почему дальше нужен другой метод

Повторный grep даст те же литералы, а не причинность. Возможные следующие методы, каждый требует согласования объёма:

- offline-анализ копии maind на компьютере: ELF, string xrefs/call graph, выбранные LED/config contexts; без запуска бинарника и без вмешательства в колонку;
- узкая выборка диагностических событий при контролируемом нажатии владельцем, только если можно исключить речь/токены и заранее согласован способ;
- отдельный визуальный эксперимент с паттернами — **меняет устройство**, сейчас запрещён.

Локальная проверка инструментов показала отсутствие objdump/readelf в PATH и Python-модулей capstone/elftools. Ничего не устанавливалось; бинарник на компьютер не копировался. Полноценный offline-анализ ещё не начат.
