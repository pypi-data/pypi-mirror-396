# RigbySDK Python

Официальный Python SDK для работы с Rigby API. Структура и методы соответствуют TypeScript SDK (`@rigbyhost/sdk-ts`), так что переносить код просто.

## Установка

```bash
pip install rigbysdk
# или локально из репозитория
pip install -e .
```

## Быстрый старт

```python
from rigbysdk import RigbySDK

sdk = RigbySDK("YOUR_API_TOKEN")

# Получить конфиг сервера
config = sdk.gdps.config.get({"srvId": "my-server-id"})

# Обновить сундуки
sdk.gdps.config.updateChests({
    "srvId": "my-server-id",
    "chestConfig": {
        "ChestSmallOrbsMin": 50,
        "ChestSmallOrbsMax": 100,
        "ChestSmallDiamondsMin": 2,
        "ChestSmallDiamondsMax": 5,
        "ChestSmallShards": [1, 2, 3, 4, 5, 6],
        "ChestSmallKeysMin": 1,
        "ChestSmallKeysMax": 3,
        "ChestSmallWait": 3600,
        "ChestBigOrbsMin": 200,
        "ChestBigOrbsMax": 400,
        "ChestBigDiamondsMin": 20,
        "ChestBigDiamondsMax": 50,
        "ChestBigShards": [1, 2, 3, 4, 5, 6],
        "ChestBigKeysMin": 1,
        "ChestBigKeysMax": 3,
        "ChestBigWait": 14400
    }
})

# Поиск уровней
levels = sdk.gdps.levels.search({
    "srvId": "my-server-id",
    "query": "demon",
})

# Текущий пользователь
me = sdk.user.me()
```

## API

- Поля и аргументы методов повторяют формы из TS SDK (Zod схемы). Передавайте те же ключи/значения.
- Методы сгруппированы так же, как в TS: `sdk.gdps.*`, `sdk.notifications.*`, `sdk.user.*`, включая вложенные `player.songs`, `gdps.server`, и т.д.

## Обработка ошибок

При ошибках HTTP или некорректном ответе выбрасывается `RigbySDKError`. Сообщение содержит статус и текст ответа (если доступно).
