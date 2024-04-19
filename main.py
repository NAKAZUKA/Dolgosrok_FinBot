# main.py
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import (get_subscriptions, create_tables, add_subscription,
                      remove_subscription, get_all_subscriptions)
from parsers import parse_reports_by_inn
from last_record import parse_last_report_by_inn
from aiocron import crontab


bot = Bot(token='YOUR_TOKEN')
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


async def send_reports(user_id, reports):
    company_name = reports['company_name']
    for report in reports["reports"]:
        message_text = (
            f"{company_name}\nОтчетность: {report['otchetnost_name']}\n"
            f"Тип документа: {report['document_type']}\n"
            f"Дата размещения: {report['approval_date']}\n"
            f"<a href=\"{report['link']}\">Перейти</a>"
        )
        await bot.send_message(user_id, message_text, parse_mode='HTML')
        await asyncio.sleep(1)


async def send_last_report(user_id, last_report):
    company_name = last_report['company_name']
    for report in last_report["reports"]:
        message_text = (
            f"{company_name}\nОтчетность: {report['otchetnost_name']}\n"
            f"Тип документа: {report['document_type']}\n"
            f"Дата размещения: {report['approval_date']}\n"
            f"<a href=\"{report['link']}\">Перейти</a>"
        )
        await bot.send_message(user_id, message_text, parse_mode='HTML')
        await asyncio.sleep(1)


@crontab('00 18 * * *')  # Запуск каждый день в 18:00
async def send_reports_daily():
    all_subscriptions = get_all_subscriptions()

    for user_id, subscriptions in all_subscriptions.items():
        for subscription in subscriptions:
            inn = subscription['inn']
            organization_name = subscription['organization_name']
            reports_data = parse_reports_by_inn(inn)
            if reports_data['reports']:
                # Отправляем отчеты пользователю
                await send_reports(
                    user_id, {'company_name': organization_name,
                              'reports': reports_data['reports']})
                await asyncio.sleep(1)
            last_report_data = parse_last_report_by_inn(inn)
            if last_report_data['reports']:
                # Отправляем последний отчет пользователю
                await send_last_report(
                    user_id, {'company_name': organization_name,
                              'reports': last_report_data['reports']})
                await asyncio.sleep(1)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Информация"),
        KeyboardButton("Поиск"),
        KeyboardButton("Подписки"),
    ]
    keyboard.add(*buttons)

    await message.answer("Добро пожаловать! Выберите действие из меню:",
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'информация')
async def process_information(message: types.Message):
    await message.answer("Добро пожаловать в Dolgosrok FinBot! "
                         "Бот позволит вам подписаться на конкретные компании "
                         "по ИНН и будет присылать уведомление о публикации отчетности. "
                         "Просто введите ИНН организации для подписки и получайте "
                         "своевременные уведомления о публикации отчетности. "
                         "Чтобы подписаться на уведомления по компании, воспользуйтесь кнопкой «Подписки», "
                         "введите ИНН и получите актуальную отчетность. Спасибо, что выбрали нашего бота!")


@dp.message_handler(lambda message: message.text.lower() == 'поиск')
async def process_search(message: types.Message):
    await message.answer("Введите ИНН организации для подписки на отчетность:")


@dp.message_handler(lambda message: message.text.lower() == 'подписки')
async def process_subscriptions(message: types.Message):
    user_id = message.from_user.id
    subs = get_subscriptions(user_id)

    if subs:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for subscription in subs:
            org_name = subscription['organization_name']
            keyboard.add(KeyboardButton(f"{org_name} - Отписаться"))
            keyboard.add(KeyboardButton(f"{org_name} - Последний отчет"))
        keyboard.add(KeyboardButton("Меню"))
        await message.answer("Ваши подписки:", reply_markup=keyboard)
    else:
        await message.answer("У вас нет активных подписок.")


@dp.message_handler(lambda message: " - Отписаться" in message.text)
async def process_unsubscribe(message: types.Message):
    org_name = message.text.split(" - Отписаться")[0]

    # Получаем user_id
    user_id = message.from_user.id

    # Удаляем подписку из базы данных
    remove_subscription(user_id, org_name)

    # Отправляем сообщение о успешной отписке
    await message.answer(f"Вы успешно отписались от рассылки от {org_name}.")


@dp.message_handler(lambda message: " - Последний отчет" in message.text)
async def process_last_report(message: types.Message):
    # Получаем имя организации из текста кнопки
    org_name = message.text.split(" - Последний отчет")[0]

    # Получаем user_id
    user_id = message.from_user.id

    # Получаем ИНН организации
    subs = get_subscriptions(user_id)
    inn = next(
        (sub['inn'] for sub in subs if sub['organization_name'] == org_name),
        None)

    if inn:
        # Получаем последний отчет для ИНН
        last_report_data = parse_last_report_by_inn(inn)

        if last_report_data['reports']:
            # Отправляем последний отчет пользователю
            await send_last_report(user_id,
                                   {'company_name': org_name,
                                    'reports': last_report_data['reports']})
        else:
            await bot.send_message(
                user_id, f"Для организации {org_name} нет доступных отчетов.")
    else:
        await bot.send_message(
            user_id, f"Не удалось найти ИНН для организации {org_name}.")


@dp.message_handler(lambda message: message.text.isdigit())
async def process_inn(message: types.Message):
    inn = message.text
    user_id = message.from_user.id

    # Проверяем, есть ли такой ИНН уже в подписках
    subs = get_subscriptions(user_id)
    existing_subscription = next(
        (sub for sub in subs if sub['inn'] == inn), None)
    await bot.send_message(user_id, "Запрос обрабатывается, подождите...")

    if existing_subscription:
        org_name = existing_subscription['organization_name']
        await bot.send_message(
            user_id, f"Вы уже подписаны на рассылку от {org_name} с ИНН {inn}.")
    else:
        # Получаем отчеты для ИНН и выводим информацию
        reports_data = parse_reports_by_inn(inn)

        if reports_data:
            # Добавляем имя организации в базу данных
            add_subscription(user_id, inn, reports_data["company_name"])

            # Отправляем сообщение об успешной подписке
            await bot.send_message(
                user_id, f"Вы успешно подписались на рассылку от "
                f"{reports_data['company_name']} с ИНН {inn}")
        else:
            await bot.send_message(
                user_id, "Для указанного ИНН нет доступных отчетов.")


@dp.message_handler(lambda message: message.text.lower() == 'меню')
async def return_to_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Информация"),
        KeyboardButton("Поиск"),
        KeyboardButton("Подписки"),
    ]
    keyboard.add(*buttons)

    await message.answer("Вы вернулись в меню!", reply_markup=keyboard)


if __name__ == '__main__':
    from aiogram import executor

    # Создаем таблицы в базе данных при первом запуске
    create_tables()

    executor.start_polling(dp, skip_updates=True)
    send_reports_daily()
