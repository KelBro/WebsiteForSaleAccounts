from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config_reader import config
from website.data import db_session
from website.data.__all_models import catalog_accounts

ADMIN_IDS = config.admins
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


class AddAccountStates(StatesGroup):
    waiting_game_name = State()
    waiting_product_name = State()
    waiting_price = State()
    waiting_description = State()
    waiting_count = State()


class EditAccountStates(StatesGroup):
    selecting_account = State()
    choosing_action = State()
    editing_field = State()
    new_value = State()


def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_accounts_keyboard():
    session = db_session.create_session()
    accounts = session.query(catalog_accounts.Catalog).all()
    session.close()

    builder = InlineKeyboardBuilder()
    for account in accounts:
        builder.add(types.InlineKeyboardButton(
            text=f"{account.game_name} - {account.product_name}",
            callback_data=f"account_{account.id}"
        ))
    builder.adjust(1)
    return builder.as_markup()


# Стартовое меню
@dp.message(Command("start"))
async def handle_start(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещен")
        return

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Добавить аккаунт"))
    builder.add(types.KeyboardButton(text="Редактировать аккаунты"))
    await message.answer("🔐 Админ-панель:", reply_markup=builder.as_markup(resize_keyboard=True))


# Меню редактирования
@dp.message(F.text == "Редактировать аккаунты")
async def handle_edit_accounts(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Выберите аккаунт для редактирования:", reply_markup=get_accounts_keyboard())
    await state.set_state(EditAccountStates.selecting_account)


# Обработка выбора аккаунта
@dp.callback_query(EditAccountStates.selecting_account, F.data.startswith("account_"))
async def handle_account_selection(callback: types.CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split("_")[1])
    await state.update_data(account_id=account_id)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✏️ Изменить", callback_data="edit"))
    builder.add(types.InlineKeyboardButton(text="🗑️ Удалить", callback_data="delete"))
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    builder.adjust(2)

    await callback.message.edit_text("Выберите действие:", reply_markup=builder.as_markup())
    await state.set_state(EditAccountStates.choosing_action)


# Обработка выбора действия
@dp.callback_query(EditAccountStates.choosing_action, F.data.in_(["edit", "delete", "cancel"]))
async def handle_action_selection(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await callback.message.delete()
        await state.clear()
        return

    data = await state.get_data()
    account_id = data['account_id']
    session = db_session.create_session()
    account = session.query(catalog_accounts.Catalog).get(account_id)

    if callback.data == "delete":
        session.delete(account)
        session.commit()
        await callback.message.edit_text("✅ Аккаунт успешно удален")
        await state.clear()
    elif callback.data == "edit":
        builder = InlineKeyboardBuilder()
        fields = ["game_name", "product_name", "price", "description", "count"]
        for field in fields:
            builder.add(types.InlineKeyboardButton(
                text=field.replace("_", " ").title(),
                callback_data=f"field_{field}"
            ))
        builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
        builder.adjust(2)

        await callback.message.edit_text("Выберите поле для редактирования:", reply_markup=builder.as_markup())
        await state.set_state(EditAccountStates.editing_field)

    session.close()


# Обработка выбора поля для редактирования
@dp.callback_query(EditAccountStates.editing_field, F.data.startswith("field_"))
async def handle_field_selection(callback: types.CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]
    await state.update_data(field=field)
    await callback.message.edit_text(f"Введите новое значение для {field.replace('_', ' ')}:")
    await state.set_state(EditAccountStates.new_value)


# Обработка нового значения
@dp.message(EditAccountStates.new_value)
async def handle_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    account_id = data['account_id']
    field = data['field']
    new_value = message.text

    session = db_session.create_session()
    account = session.query(catalog_accounts.Catalog).get(account_id)

    try:
        # Преобразуем числовые поля
        if field in ["price", "count"]:
            new_value = int(new_value)

        setattr(account, field, new_value)
        session.commit()

        await message.answer(f"✅ Поле {field.replace('_', ' ')} успешно обновлено")
    except ValueError:
        await message.answer("❌ Неверный формат значения")
    finally:
        session.close()

    await state.clear()

@dp.message(F.text == "Добавить аккаунт")
async def handle_add_account(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AddAccountStates.waiting_game_name)
    await message.answer("Введите название игры:")


@dp.message(AddAccountStates.waiting_game_name)
async def handle_game_name(message: types.Message, state: FSMContext):
    await state.update_data(game_name=message.text)
    await state.set_state(AddAccountStates.waiting_product_name)
    await message.answer("Введите название продукта:")


@dp.message(AddAccountStates.waiting_product_name)
async def handle_product_name(message: types.Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await state.set_state(AddAccountStates.waiting_price)
    await message.answer("Введите цену (только число):")


@dp.message(AddAccountStates.waiting_price)
async def handle_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await state.set_state(AddAccountStates.waiting_count)
        await message.answer("Введите количество(только число):")
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")

@dp.message(AddAccountStates.waiting_count)
async def handle_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        await state.update_data(count=count)
        await state.set_state(AddAccountStates.waiting_description)
        await message.answer("Введите описание:")
    except ValueError:
        await message.answer("❌ Неверный формат количества. Введите число:")


@dp.message(AddAccountStates.waiting_description)
async def handle_password(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()

        session = db_session.create_session()
        new_account = catalog_accounts.Catalog(
            game_name=user_data['game_name'],
            product_name=user_data['product_name'],
            price=user_data['price'],
            description=message.text,
            count=user_data['count'],
        )
        session.add(new_account)
        session.commit()
        session.close()

        await state.clear()

        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Добавить аккаунт"))

        await message.answer(
            f"✅ Аккаунт добавлен:\n\n"
            f"🎮 Игра: {user_data['game_name']}\n"
            f"📦 Продукт: {user_data['product_name']}\n"
            f"💵 Цена: {user_data['price']} ₽\n"
            f"📝 Описание: {message.text}\n"
            f"📚 Количество: {user_data['count']}",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        if 'session' in locals():
            session.close()
        await state.clear()

async def run_bot():
    await dp.start_polling(bot)