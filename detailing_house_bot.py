"""
Telegram-бот для Detailing House (Екатеринбург / Североуральск)
Библиотека: aiogram v3
Запуск: polling
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Contact,
)

# ──────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────
BOT_TOKEN         = os.getenv("BOT_TOKEN", "8636489331:AAHMz-VvBtsh2rOQ5lQq7JrjEJ5B__XXOO4")
ADMIN_CHAT_ID     = 1375530733
MANAGER_USERNAME  = "@DetailingHouseEkb"
MANAGER_PHONE_EKB = "+7 (993) 773-57-71"
MANAGER_PHONE_SVU = "+7 (908) 922-88-96"
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
router = Router()
user_data: dict[int, dict] = {}

# ──────────────────────────────────────────────
# Шаги диалога
# ──────────────────────────────────────────────
STEP_IDLE       = "idle"
STEP_SERVICE    = "service"
STEP_SUBTYPE    = "subtype"    # выбор конкретной услуги
STEP_SUBCLASS   = "subclass"   # выбор класса авто
STEP_CAR        = "car"
STEP_TASK       = "task"
STEP_PHONE      = "phone"
STEP_DONE       = "done"

# ──────────────────────────────────────────────
# Списки услуг
# ──────────────────────────────────────────────

WASH_TYPES = [
    "1️⃣ Однофазная мойка",
    "2️⃣ Двухфазная мойка",
    "3️⃣ Трёхфазная мойка",
    "✨ Комплекс «Стандарт»",
    "🔹 Комплекс «Детейлинг мойка»",
]

POLISH_TYPES = [
    "🔧 Коррекционная полировка ЛКП",
    "💎 Комплексная полировка ЛКП",
    "📍 Локальная полировка элемента",
    "💡 Полировка фар и оптики",
    "🪨 Твёрдый воск",
    "🔵 Керамическое покрытие",
]

INTERIOR_TYPES = [
    "🧹 Комплексная химчистка салона",
    "☁️ Химчистка потолка",
    "🪵 Химчистка пола (с разбором)",
    "🪵 Химчистка пола (без разбора)",
    "🚪 Химчистка дверной карты",
    "💺 Химчистка сидений (ткань/кожа)",
    "🌀 Озонирование салона",
    "💨 Сухой туман (устранение запахов)",
]

CAR_CLASSES = [
    "🚗 1 класс (хэтчбеки, B/C)",
    "🚙 2 класс (кроссоверы, D/E)",
    "🚐 3 класс (внедорожники, премиум)",
]

# ──────────────────────────────────────────────
# Прайсы
# ──────────────────────────────────────────────

WASH_PRICES = {
    "1️⃣ Однофазная мойка": {
        "desc": "Бесконтактный шампунь, сушка кузова, продувка замков и ручек, чистка ковриков",
        "🚗 1 класс (хэтчбеки, B/C)":        "600 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "700 ₽",
        "🚐 3 класс (внедорожники, премиум)": "800 ₽",
    },
    "2️⃣ Двухфазная мойка": {
        "desc": "Бесконтактный + ручной шампунь, сушка кузова, продувка замков и ручек",
        "🚗 1 класс (хэтчбеки, B/C)":        "1 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "1 200 ₽",
        "🚐 3 класс (внедорожники, премиум)": "1 300 ₽",
    },
    "3️⃣ Трёхфазная мойка": {
        "desc": "Двухфазная мойка + уборка салона + консервация жидким воском",
        "🚗 1 класс (хэтчбеки, B/C)":        "1 300 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "1 500 ₽",
        "🚐 3 класс (внедорожники, премиум)": "1 600 ₽",
    },
    "✨ Комплекс «Стандарт»": {
        "desc": "Двухфазная мойка, пылесос, уборка салона, полироль пластика, чистка стёкол, чистка ковров",
        "🚗 1 класс (хэтчбеки, B/C)":        "2 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "2 200 ₽",
        "🚐 3 класс (внедорожники, премиум)": "2 400 ₽",
    },
    "🔹 Комплекс «Детейлинг мойка»": {
        "desc": "Двухфазная мойка, удаление битума/вкраплений, химчистка стёкол/дисков/арок, кварцевое покрытие",
        "🚗 1 класс (хэтчбеки, B/C)":        "3 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "3 500 ₽",
        "🚐 3 класс (внедорожники, премиум)": "4 000 ₽",
    },
}

POLISH_PRICES = {
    "🔧 Коррекционная полировка ЛКП": {
        "desc": "2-х фазная абразивная. Двухфазная мойка, удаление битума/смол, скрабирование глиной, обезжиривание",
        "🚗 1 класс (хэтчбеки, B/C)":        "12 000 – 15 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "15 000 – 18 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "18 000 – 25 000 ₽",
    },
    "💎 Комплексная полировка ЛКП": {
        "desc": "3-х фазная абразивная. Максимальное восстановление блеска и устранение дефектов ЛКП",
        "🚗 1 класс (хэтчбеки, B/C)":        "15 000 – 18 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "18 000 – 21 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "21 000 – 28 000 ₽",
    },
    "📍 Локальная полировка элемента": {
        "desc": "Полировка отдельного элемента кузова (крыло, дверь, капот и т.д.)",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 500 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 500 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 500 ₽",
    },
    "💡 Полировка фар и оптики": {
        "desc": "Восстановление прозрачности пластиковых фар и оптики",
        "🚗 1 класс (хэтчбеки, B/C)":        "2 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "2 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "2 000 ₽",
    },
    "🪨 Твёрдый воск": {
        "desc": "Рекомендуется после полировки или улучшенной мойки",
        "🚗 1 класс (хэтчбеки, B/C)":        "3 500 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "4 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "4 500 ₽",
    },
    "🔵 Керамическое покрытие": {
        "desc": "Рекомендуется после полировки. Долгосрочная защита ЛКП",
        "🚗 1 класс (хэтчбеки, B/C)":        "10 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "12 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "14 000 ₽",
    },
}

INTERIOR_PRICES = {
    "🧹 Комплексная химчистка салона": {
        "desc": "Потолок, козырьки, стойки, дверные карты, пластик, сиденья, стёкла + нейтрализатор/крем",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 8 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 10 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 12 000 ₽",
    },
    "☁️ Химчистка потолка": {
        "desc": "Глубокая химчистка потолочного покрытия",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 2 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 2 300 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 2 600 ₽",
    },
    "🪵 Химчистка пола (с разбором)": {
        "desc": "Химчистка напольного покрытия с разбором сидений и накладок",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 4 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 4 500 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 5 000 ₽",
    },
    "🪵 Химчистка пола (без разбора)": {
        "desc": "Химчистка напольного покрытия без разбора сидений",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 3 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 3 500 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 4 000 ₽",
    },
    "🚪 Химчистка дверной карты": {
        "desc": "Чистка внутренней обшивки дверей",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 300 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 300 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 300 ₽",
    },
    "💺 Химчистка сидений (ткань/кожа)": {
        "desc": "Глубокая чистка сидений из ткани или кожи",
        "🚗 1 класс (хэтчбеки, B/C)":        "от 800 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "от 800 ₽",
        "🚐 3 класс (внедорожники, премиум)": "от 800 ₽",
    },
    "🌀 Озонирование салона": {
        "desc": "Устранение запахов (табак, животные, плесень и др.) с помощью озона",
        "🚗 1 класс (хэтчбеки, B/C)":        "1 000 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "1 000 ₽",
        "🚐 3 класс (внедорожники, премиум)": "1 000 ₽",
    },
    "💨 Сухой туман (устранение запахов)": {
        "desc": "Нейтрализация запахов методом сухого тумана",
        "🚗 1 класс (хэтчбеки, B/C)":        "600 ₽",
        "🚙 2 класс (кроссоверы, D/E)":       "700 ₽",
        "🚐 3 класс (внедорожники, премиум)": "800 ₽",
    },
}

# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────

def kb_main() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚿 Мойка"),            KeyboardButton(text="💎 Полировка ЛКП")],
        [KeyboardButton(text="🧹 Химчистка салона"), KeyboardButton(text="🪟 Стёкла / Антидождь")],
        [KeyboardButton(text="🔧 Подкапотка / Днище"), KeyboardButton(text="📦 Другое")],
        [KeyboardButton(text="📋 Прайс")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_list(items: list[str], back: bool = True) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=item)] for item in items]
    if back:
        buttons.append([KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_car_class() -> ReplyKeyboardMarkup:
    return kb_list(CAR_CLASSES)


def kb_price_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚿 Прайс: Мойка"),         KeyboardButton(text="💎 Прайс: Полировка ЛКП")],
        [KeyboardButton(text="🧹 Прайс: Химчистка"),     KeyboardButton(text="🪟 Прайс: Стёкла")],
        [KeyboardButton(text="🔧 Прайс: Подкапотка / Днище")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_phone() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text="📞 Отправить номер", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def kb_after_order() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📞 Позвонить в ЕКБ"), KeyboardButton(text="📞 Позвонить в СВУ")],
        [KeyboardButton(text="💬 Написать в Telegram")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ──────────────────────────────────────────────
# Хелперы
# ──────────────────────────────────────────────

def get_step(user_id: int) -> str:
    return user_data.get(user_id, {}).get("step", STEP_IDLE)

def set_step(user_id: int, step: str) -> None:
    user_data.setdefault(user_id, {})["step"] = step

def save_field(user_id: int, key: str, value) -> None:
    user_data.setdefault(user_id, {})[key] = value

def reset_user(user_id: int) -> None:
    user_data[user_id] = {"step": STEP_IDLE}

def get_price_dict(category: str) -> dict:
    if category == "wash":
        return WASH_PRICES
    elif category == "polish":
        return POLISH_PRICES
    elif category == "interior":
        return INTERIOR_PRICES
    return {}

# ──────────────────────────────────────────────
# Хэндлеры — /start
# ──────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    reset_user(message.from_user.id)
    set_step(message.from_user.id, STEP_SERVICE)
    await message.answer(
        "👋 Добро пожаловать в <b>Detailing House</b>!\n"
        "Екатеринбург / Североуральск\n\n"
        "Выберите нужную услугу или посмотрите прайс 👇\n\n"
        "💳 Доступна оплата <b>ДОЛЯМИ</b> до 200 000 ₽",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Прайс
# ──────────────────────────────────────────────

@router.message(F.text == "📋 Прайс")
async def show_price(message: Message) -> None:
    await message.answer(
        "📋 <b>Прайс-лист Detailing House</b>\n\nВыберите категорию 👇",
        parse_mode="HTML",
        reply_markup=kb_price_menu(),
    )

@router.message(F.text == "🚿 Прайс: Мойка")
async def price_wash_menu(message: Message) -> None:
    await message.answer(
        "🚿 <b>Прайс: Мойки</b>\n\n"
        "1️⃣ <b>Однофазная</b> — 600 / 700 / 800 ₽\n"
        "<i>Бесконтактный шампунь, сушка, продувка, коврики</i>\n\n"
        "2️⃣ <b>Двухфазная</b> — 1 000 / 1 200 / 1 300 ₽\n"
        "<i>Бесконтакт + ручной шампунь, сушка, продувка</i>\n\n"
        "3️⃣ <b>Трёхфазная</b> — 1 300 / 1 500 / 1 600 ₽\n"
        "<i>Двухфазная + уборка салона + жидкий воск</i>\n\n"
        "✨ <b>Комплекс «Стандарт»</b> — 2 000 / 2 200 / 2 400 ₽\n"
        "<i>Двухфазная, пылесос, уборка салона, полироль пластика, стёкла</i>\n\n"
        "🔹 <b>Комплекс «Детейлинг мойка»</b> — 3 000 / 3 500 / 4 000 ₽\n"
        "<i>Двухфазная, удаление битума, химчистка стёкол/дисков/арок, кварц-защита</i>\n\n"
        "<i>Цены: 1 класс / 2 класс / 3 класс</i>",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

@router.message(F.text == "💎 Прайс: Полировка ЛКП")
async def price_polish_menu(message: Message) -> None:
    await message.answer(
        "💎 <b>Прайс: Полировка ЛКП</b>\n\n"
        "🔧 <b>Коррекционная</b> — 12-15k / 15-18k / 18-25k ₽\n"
        "💎 <b>Комплексная</b> — 15-18k / 18-21k / 21-28k ₽\n"
        "📍 <b>Локальная (элемент)</b> — от 500 ₽\n"
        "💡 <b>Полировка фар</b> — 2 000 ₽\n"
        "🪨 <b>Твёрдый воск</b> — 3 500 / 4 000 / 4 500 ₽\n"
        "🔵 <b>Керамика</b> — 10 000 / 12 000 / 14 000 ₽\n\n"
        "<i>Цены: 1 класс / 2 класс / 3 класс</i>",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

@router.message(F.text == "🧹 Прайс: Химчистка")
async def price_interior_menu(message: Message) -> None:
    await message.answer(
        "🧹 <b>Прайс: Химчистка салона</b>\n\n"
        "🧹 <b>Комплексная</b> — от 8 000 / 10 000 / 12 000 ₽\n"
        "☁️ <b>Потолок</b> — от 2 000 / 2 300 / 2 600 ₽\n"
        "🪵 <b>Пол (с разбором)</b> — от 4 000 / 4 500 / 5 000 ₽\n"
        "🪵 <b>Пол (без разбора)</b> — от 3 000 / 3 500 / 4 000 ₽\n"
        "🚪 <b>Дверная карта</b> — от 300 ₽\n"
        "💺 <b>Сиденья (ткань/кожа)</b> — от 800 ₽\n"
        "🌀 <b>Озонирование</b> — 1 000 ₽\n"
        "💨 <b>Сухой туман</b> — 600 / 700 / 800 ₽\n\n"
        "<i>Цены: 1 класс / 2 класс / 3 класс</i>",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

@router.message(F.text == "🪟 Прайс: Стёкла")
async def price_glass(message: Message) -> None:
    await message.answer(
        "🪟 <b>ПОЛИРОВКА СТЕКЛА</b>\n\n"
        "├ <b>Лобовое / заднее (освежающая)</b> — <b>от 3 000 ₽</b>\n"
        "├ <b>Боковое (освежающая)</b> — <b>от 1 500 ₽</b>\n"
        "└ <b>Боковое (глубокая)</b> — <b>от 2 500 ₽</b>\n\n"
        "🌧 <b>АНТИДОЖДЬ</b>\n"
        "<i>Самоочистка стёкол, срыв капель от 80 км/ч</i>\n\n"
        "├ <b>Лобовое / заднее</b> — <b>1 300 ₽</b>\n"
        "├ <b>Боковое стекло</b> — <b>400 ₽</b>\n"
        "├ <b>Полусфера</b> — <b>2 000 ₽</b>\n"
        "└ <b>Полное остекление</b> — <b>3 500 ₽</b>\n\n"
        "📝 <b>Хотите записаться?</b> Выберите услугу в меню 👇",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

@router.message(F.text == "🔧 Прайс: Подкапотка / Днище")
async def price_engine(message: Message) -> None:
    await message.answer(
        "🔧 <b>ХИМЧИСТКА ПОДКАПОТКИ</b>\n"
        "<i>Гель-диэлектрик, щелочной очиститель, консервант</i>\n\n"
        "├ <b>Подкапотное пространство (верх)</b>\n"
        "│  1 кл — от 3 000 ₽  |  2 кл — от 3 500 ₽  |  3 кл — от 4 000 ₽\n\n"
        "├ <b>Подкапотное пространство (низ)</b>\n"
        "│  1 кл — от 3 500 ₽  |  2 кл — от 4 000 ₽  |  3 кл — от 4 500 ₽\n\n"
        "🔧 <b>МОЙКА ДНИЩА НА ЭСТАКАДЕ</b>\n\n"
        "└ 1 кл — от 4 000 ₽  |  2 кл — от 4 500 ₽  |  3 кл — от 5 000 ₽\n\n"
        "📝 <b>Хотите записаться?</b> Выберите услугу в меню 👇",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Запись: шаг 1 — выбор категории
# ──────────────────────────────────────────────

@router.message(F.text == "🚿 Мойка")
async def handle_wash(message: Message) -> None:
    user_id = message.from_user.id
    save_field(user_id, "category", "wash")
    set_step(user_id, STEP_SUBTYPE)
    await message.answer(
        "🚿 <b>Выберите вид мойки</b> 👇",
        parse_mode="HTML",
        reply_markup=kb_list(WASH_TYPES),
    )

@router.message(F.text == "💎 Полировка ЛКП")
async def handle_polish(message: Message) -> None:
    user_id = message.from_user.id
    save_field(user_id, "category", "polish")
    set_step(user_id, STEP_SUBTYPE)
    await message.answer(
        "💎 <b>Выберите вид полировки</b> 👇",
        parse_mode="HTML",
        reply_markup=kb_list(POLISH_TYPES),
    )

@router.message(F.text == "🧹 Химчистка салона")
async def handle_interior(message: Message) -> None:
    user_id = message.from_user.id
    save_field(user_id, "category", "interior")
    set_step(user_id, STEP_SUBTYPE)
    await message.answer(
        "🧹 <b>Выберите вид химчистки</b> 👇",
        parse_mode="HTML",
        reply_markup=kb_list(INTERIOR_TYPES),
    )

@router.message(F.text.in_(["🪟 Стёкла / Антидождь", "🔧 Подкапотка / Днище", "📦 Другое"]))
async def handle_other_service(message: Message) -> None:
    user_id = message.from_user.id
    save_field(user_id, "service", message.text)
    set_step(user_id, STEP_CAR)
    await message.answer(
        f"Отлично! Вы выбрали: <b>{message.text}</b>\n\n"
        "🚗 Какой у вас автомобиль? Напишите марку и модель\n"
        "<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Запись: шаг 2 — выбор конкретной услуги
# ──────────────────────────────────────────────

ALL_SUBTYPES = WASH_TYPES + POLISH_TYPES + INTERIOR_TYPES

@router.message(F.text.in_(ALL_SUBTYPES))
async def handle_subtype(message: Message) -> None:
    user_id = message.from_user.id
    if get_step(user_id) != STEP_SUBTYPE:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return
    save_field(user_id, "subtype", message.text)
    set_step(user_id, STEP_SUBCLASS)
    await message.answer(
        f"Выбрано: <b>{message.text}</b>\n\n"
        "🚗 Теперь выберите класс вашего автомобиля 👇\n\n"
        "<b>1 класс</b> — хэтчбеки, седаны B/C (Polo, Rio, Solaris...)\n"
        "<b>2 класс</b> — кроссоверы, минивэны, D/E (Camry, Tiguan, X5...)\n"
        "<b>3 класс</b> — внедорожники, премиум (LC, G-class, S-class...)",
        parse_mode="HTML",
        reply_markup=kb_car_class(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Запись: шаг 3 — выбор класса → показ цены
# ──────────────────────────────────────────────

@router.message(F.text.in_(CAR_CLASSES))
async def handle_car_class(message: Message) -> None:
    user_id = message.from_user.id
    if get_step(user_id) != STEP_SUBCLASS:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return

    car_class = message.text
    category  = user_data.get(user_id, {}).get("category", "")
    subtype   = user_data.get(user_id, {}).get("subtype", "")

    price_dict = get_price_dict(category)
    info  = price_dict.get(subtype, {})
    price = info.get(car_class, "—")
    desc  = info.get("desc", "")

    save_field(user_id, "service", f"{subtype} ({car_class})")
    set_step(user_id, STEP_CAR)

    await message.answer(
        f"✅ <b>{subtype}</b>\n"
        f"🚗 {car_class}\n\n"
        f"💰 Стоимость: <b>{price}</b>\n"
        f"<i>{desc}</i>\n\n"
        "Напишите марку и модель вашего автомобиля\n"
        "<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Запись: шаги 4-5 — авто, задача, телефон
# ──────────────────────────────────────────────

@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_id = message.from_user.id
    step    = get_step(user_id)

    if step == STEP_CAR:
        save_field(user_id, "car", message.text)
        set_step(user_id, STEP_TASK)
        await message.answer(
            "📝 Опишите задачу подробнее:\n\n"
            "<i>Например: убрать царапины, сильное загрязнение салона, запах в авто</i>",
            parse_mode="HTML",
        )
        return

    if step == STEP_TASK:
        save_field(user_id, "task", message.text)
        set_step(user_id, STEP_PHONE)
        await message.answer(
            "📞 Последний шаг — оставьте ваш номер телефона.\n"
            "Нажмите кнопку ниже:",
            reply_markup=kb_phone(),
        )
        return

    if message.text == "📞 Позвонить в ЕКБ":
        await message.answer(
            f"Звоните нам в Екатеринбурге 📞\n<b>{MANAGER_PHONE_EKB}</b>",
            parse_mode="HTML", reply_markup=kb_after_order(),
        )
        return

    if message.text == "📞 Позвонить в СВУ":
        await message.answer(
            f"Звоните нам в Североуральске 📞\n<b>{MANAGER_PHONE_SVU}</b>",
            parse_mode="HTML", reply_markup=kb_after_order(),
        )
        return

    if message.text == "💬 Написать в Telegram":
        await message.answer(
            f"Напишите нашему менеджеру: <b>{MANAGER_USERNAME}</b>\n"
            f"👉 https://t.me/{MANAGER_USERNAME.lstrip('@')}",
            parse_mode="HTML", reply_markup=kb_after_order(),
        )
        return

    if message.text == "🏠 Главное меню":
        reset_user(user_id)
        set_step(user_id, STEP_SERVICE)
        await message.answer("Главное меню 👇", reply_markup=kb_main())
        return

    await message.answer(
        "Пожалуйста, используйте кнопки меню или начните с /start",
        reply_markup=kb_main(),
    )

# ──────────────────────────────────────────────
# Хэндлеры — Контакт
# ──────────────────────────────────────────────

@router.message(F.contact)
async def handle_contact(message: Message) -> None:
    user_id = message.from_user.id

    if get_step(user_id) != STEP_PHONE:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return

    contact: Contact = message.contact
    phone = contact.phone_number
    save_field(user_id, "phone", phone)
    set_step(user_id, STEP_DONE)

    data = user_data.get(user_id, {})
    admin_text = (
        "🚗 <b>НОВАЯ ЗАЯВКА — Detailing House</b>\n\n"
        f"Услуга: {data.get('service', '—')}\n"
        f"Авто: {data.get('car', '—')}\n"
        f"Описание: {data.get('task', '—')}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{message.from_user.username or 'нет username'}\n"
        f"Имя: {message.from_user.full_name}"
    )

    try:
        await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logging.warning(f"Не удалось отправить заявку администратору: {e}")

    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n\n"
        "Если хотите связаться прямо сейчас — выберите удобный способ 👇",
        parse_mode="HTML",
        reply_markup=kb_after_order(),
    )

# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────

async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
