from aiogram.filters.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSM(StatesGroup):
    # Создаем экземпляры класса State для группы состояний FSM,
    # последовательно перечисляя возможные состояния, в которых будет 
    # находиться бот в разные моменты взаимодейтсвия с пользователем
    start = State()             # игрок начал игру