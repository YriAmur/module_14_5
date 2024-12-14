from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import crud_functions_14_5
import re


crud_functions_14_5.initiate_db()
products = crud_functions_14_5.get_all_products()

api = ""
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())


# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [KeyboardButton(text='Купить')],
        [KeyboardButton(text='Регистрация')]
    ], resize_keyboard=True
)

kb_inl = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
        ]
    ], resize_keyboard=True
)

kb_buy = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Produkt1', callback_data='buying'),
            InlineKeyboardButton('Produkt2', callback_data='buying'),
            InlineKeyboardButton('Produkt3', callback_data='buying'),
            InlineKeyboardButton('Produkt4', callback_data='buying')
        ]
    ], resize_keyboard=True
)
# Функция /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

# Функция для обработки нажатия кнопки 'Рассчитать'
@dp.message_handler(text=['Рассчитать'])
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inl)

# Функция для обработки нажатия кнопки 'Информация'
@dp.message_handler(text=['Информация'])
async def info(message: types.Message):
    await message.answer('Данный бот рассчитает суточную норму потребления калорий')

# Функция для получения формул
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора:\n"
                    "Для мужчин:\n"
                    "BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                    "Для женщин:\n"
                    "BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161")
    await call.message.answer(formula_text)
    await call.answer()

# Функция для установки возраста по нажатой Inline кнопке
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()  # Переход к состоянию

# Функция для установки роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохранение возраста
    await message.answer('Введите свой рост:')
    await UserState.growth.set()  # Переход к состоянию growth

# Функция для установки веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Сохранение роста
    await message.answer('Введите свой вес:')
    await UserState.weight.set()  # Переход к состоянию weight


# Функция для отправки калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Сохранение веса



    data = await state.get_data()  # Получение всех введенных данных
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора (для мужчин)
    # BMR = 10 * weight + 6.25 * height - 5 * age + 5
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {bmr} калорий.')

    await state.finish()  # Завершение состояний

@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    for product in products:
        id, title, description, price = product
        await message.answer(f'Номер: {id} |'
                             f'Название: {title} | '
                             f'Описание: {description} | '
                             f'Цена: {price}')
        with open(f'files/{id}.jpeg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:',
                         reply_markup=kb_buy)


@dp.callback_query_handler(text='buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.message_handler(text=['Регистрация'])
async def sign_up(message: types.Message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    if crud_functions_14_5.is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        return
    await state.update_data(username=message.text)
    await message.answer('Введите свой email:')
    await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    crud_functions_14_5.add_user(data['username'], data['email'], data['age'])
    await message.answer(f'Пользователь {data["username"]} зарегистрирован.')
    await state.finish()

@dp.message_handler()
async def all_message(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)