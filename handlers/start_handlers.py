from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from lexicon.lexicon import LEXICON, LEXICON_BTN
from keywords.kb_inline import create_inline_kb
from services.fsm_states import FSM
from services.functions import get_number


router: Router = Router() # Подключаем роутер

games: dict[dict[str,any]] = {}
game_field: list[str] = list(map(str, range(9)))
victory: list[set] = [{0,1,2},
                      {3,4,5},
                      {6,7,8},
                      {2,4,6},
                      {0,4,8},
                      {0,3,6},
                      {1,4,7},
                      {2,5,8}]

def is_victory(field: list, role: str) -> bool:
    positions: set= set()
    for i in range(len(field)):
        if field[i] == LEXICON_BTN[role]:
            positions.add(i)
    for variant in victory:
        if variant.issubset(positions):
            return True    
    return False

def is_draw(field: list) -> bool:
    for row in field:
        if row not in [LEXICON_BTN['x'], LEXICON_BTN['o']]:
            return False
    return True
    

# Приветствие
@router.message(CommandStart())
async def start_bot(message: Message, state: FSMContext, bot: Bot):
    if message.text.replace('/start', '').strip() and games.get(message.text.replace('/start', '').strip()):
        if message.chat.id != games[message.text.replace('/start', '').strip()]['player1']:
            await state.clear()
            await get_join_code(message, state, bot)
        else:
            await message.answer(text=LEXICON['link'])
    else:
        await message.answer(LEXICON['/start'])
    

# Справка об игре
@router.message(Command(commands='help'))
async def get_help(message: Message, state: FSMContext):
    await message.answer(LEXICON['/help'])


# сдаться
@router.message(Command(commands='end'), StateFilter(FSM.start))
async def end_game(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data:
        game: str = data['game']
        if games.get(game):
            if games[game]['player1'] == message.chat.id:
                games[game]['status'] = 'finished'
                games[game]['winner'] = games[game]['player2']
            elif games[game]['player2'] == message.chat.id:
                games[game]['status'] = 'finished'
                games[game]['winner'] = games[game]['player1']
    await message.answer(text=LEXICON['game_over'])
    await state.clear() 


# Начать игру
@router.message(Command(commands='new'), StateFilter(default_state))
async def start_game(message: Message, state: FSMContext, bot: Bot):
    game_number: str = get_number()
    await state.update_data(game=game_number)
    await message.answer(LEXICON['/new'])
    bot_name = await bot.get_me()
    await message.answer(f'{LEXICON["link_name"]}https://t.me/{bot_name.username}?start={game_number}')
    games[game_number] = dict(number=game_number, player1=message.from_user.id, player2='', 
                      status='create', winner='', kb=game_field.copy(), step='')
    await state.set_state(FSM.start)


# Попытка начать другую игру в состоянии игры
@router.message(Command(commands=['new']), ~StateFilter(default_state))
async def start_game_not_finished(message: Message, state: FSMContext):
    await message.answer('Вы не завершили еще игру. \nДля завершения нажмите /end')


# Ввод кода игры
async def get_join_code(message: Message, state: FSMContext, bot: Bot):
    game: str = message.text.replace('/start', '').strip()
    await state.update_data(game=game)
    if games[game]['status'] == 'create':
        games[game]['player2'] = message.from_user.id
        games[game]['status'] = 'started'
        await bot.send_message(games[game]['player1'], text=LEXICON['your_step'],
                                reply_markup=create_inline_kb(3, *games[game]['kb']))
        await bot.send_message(games[game]['player2'], text=LEXICON['start_game'],
                                                    reply_markup=create_inline_kb(3, *games[game]['kb']))
        await bot.send_message(games[game]['player2'], text=LEXICON['not_your_step'])
        games[game]['step'] = games[game]['player1']
        await state.set_state(FSM.start)
    else:
        await message.answer(LEXICON['late'])

        
# Ход игроков
@router.callback_query(StateFilter(FSM.start))
async def get_step_by_1(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    game: str = data['game']
    btn_data: str = callback.data
    if btn_data in list(map(str, range(9))):
        btn: int = int(btn_data)
        if games[game]['step'] == callback.from_user.id:
            if games[game]['player1'] == callback.from_user.id:
                games[game]['kb'][btn] = LEXICON_BTN['x']
                if is_victory(games[game]['kb'], 'x'):
                    await callback.message.edit_text(text=LEXICON['victory'],
                                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.answer(text=LEXICON['victory'], show_alert=True)
                    await bot.send_message(chat_id=games[game]['player2'], text=LEXICON['loss'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['status'] = 'finished'
                    games[game]['winner'] = games[game]['player1']
                    await state.clear()
                elif is_draw(games[game]['kb']):
                    await callback.message.edit_text(text=LEXICON['draw'],
                                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.answer(text=LEXICON['draw'], show_alert=True)
                    await bot.send_message(chat_id=games[game]['player2'], text=LEXICON['draw'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['status'] = 'finished'
                    games[game]['winner'] = 'draw'
                    await state.clear()
                else:
                    await bot.send_message(chat_id=games[game]['player2'], text=LEXICON['your_step'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.message.edit_reply_markup(reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['step'] = games[game]['player2']

            elif games[game]['player2'] == callback.from_user.id:
                games[game]['kb'][btn] = LEXICON_BTN['o']
                if is_victory(games[game]['kb'], 'o'):
                    await callback.message.edit_text(text=LEXICON['victory'],
                                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.answer(text=LEXICON['victory'], show_alert=True)
                    await bot.send_message(chat_id=games[game]['player1'], text=LEXICON['loss'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['status'] = 'finished'
                    games[game]['winner'] = games[game]['player2']
                    await state.clear()
                elif is_draw(games[game]['kb']):
                    await callback.message.edit_text(text=LEXICON['draw'],
                                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.answer(text=LEXICON['draw'], show_alert=True)
                    await bot.send_message(chat_id=games[game]['player1'], text=LEXICON['draw'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['status'] = 'finished'
                    games[game]['winner'] = 'draw'
                    await state.clear()
                else:
                    await bot.send_message(chat_id=games[game]['player1'], text=LEXICON['your_step'],
                                        reply_markup=create_inline_kb(3, *games[game]['kb']))
                    await callback.message.edit_reply_markup(reply_markup=create_inline_kb(3, *games[game]['kb']))
                    games[game]['step'] = games[game]['player1']
        else:
            await callback.answer(text=LEXICON['not_your_step'], show_alert=True)
    else:
        await callback.answer(text=LEXICON['busy'], show_alert=True)