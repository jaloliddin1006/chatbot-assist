from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    age = State()
    sex = State()
    about = State()
    photo = State()


class ChatStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_question = State()


class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()