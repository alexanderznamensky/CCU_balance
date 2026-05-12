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
3. Добавьте интеграцию через UI: **Настройки → Устройства и службы → Добавить интеграцию → Баланс CCU контроллера**.
4. Введите логин, пароль и интервал обновления.

Атрибуты сенсора:

- `ok`
- `status`
- `raw_balance`
- `login`
