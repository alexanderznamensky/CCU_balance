# Баланс контроллера CCU для Home Assistant
<img width="835" height="198" alt="image" src="https://github.com/user-attachments/assets/e5b38200-9fb6-43fe-b132-067dbeee4c37" />

Разработка https://radsel.ru/ и https://radsel.ru/products/ccurelay.html

Кастомная интеграция получает баланс с `https://ccu.su/data.cgx` командой:

```json
{"Command":"GetStateAndEvents"}
```

## Установка

1. Скопируйте папку `custom_components/ccu_balance` в `/config/custom_components/ccu_balance`.
2. Перезапустите Home Assistant.
3. Добавьте интеграцию через UI: **Настройки → Устройства и службы → Добавить интеграцию → CCU Balance**.
4. Введите логин, пароль и интервал обновления.

## Что исправлено в версии 1.0.1

- В `DataUpdateCoordinator` добавлен обязательный параметр `config_entry=entry`.
- Исправлен `OptionsFlow`: больше нет присваивания в `self.config_entry`, потому что в новых версиях Home Assistant это read-only свойство.
- Запросы выполняются асинхронно через `aiohttp`, без блокировки event loop Home Assistant.

## Поведение

Если API возвращает ошибку, `NotValid`, пустой баланс или нечисловое значение, сенсор показывает `0.0`, как в исходном скрипте.

Атрибуты сенсора:

- `ok`
- `status`
- `raw_balance`
- `login`
