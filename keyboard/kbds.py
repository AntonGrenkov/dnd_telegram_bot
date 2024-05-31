from common.consts import level_table, dice_faces
from database.models import Character
from keyboard.reply import get_keyboard
from keyboard.inline import get_callback_buttons

from database.models import Attack


cancel_kb = get_keyboard('Отмена')
skip_cancel_kb = get_keyboard('Пропустить', 'Отмена')

btns = {'Добавить расу': 'add_new_race',
        'Список рас': 'race_list',
        'Добавить класс': 'add_new_class',
        'Список классов': 'class_list',
        'Добавить вид урона': 'add_new_damage',
        'Список видов урона': 'damage_list',
        'Добавить/изменить баннер': 'add_banner',
        'Список баннеров': 'banner_list'}
admin_kb = get_callback_buttons(btns=btns, sizes=(2,))


dice_choice_buttons = {face: f'dice_{face}' for face in dice_faces}
dice_choice_buttons['Хватит кубиков'] = 'skip_dice'
dice_choice_kb = get_callback_buttons(btns=dice_choice_buttons, sizes=(6, 1))


def get_attack_kb(attacks: list[Attack]):
    attack_btns = {attack.name: f'do_attack_{attack.id}' for attack in attacks}
    attack_kb = get_callback_buttons(btns=attack_btns, sizes=(1,))
    return attack_kb


def get_character_page(character: Character):
    media = character.image
    stats = character.stats
    print(stats)
    caption = (
            f'<strong>{character.name}</strong> | '
            f'{character.race}({character.battle_class})\n'
            f'{character.level} уроверь'
            f'({str(character.exp)}/'
            f'{str(level_table[str(character.level)])})\n'
            f'C - {stats["strength"]} | Л - {stats["dexterity"]}\n'
            f'Т - {stats["constitution"]} | '
            f'И - {stats["intelligence"]}\n'
            f'М - {stats["wisdom"]} | Х - {stats["charisma"]}'
        )
    btns = {'Атаковать': f'attack_{character.id}',
            'Добавить атаку': f'add_attack_{character.id}',
            'Начислить опыт': f'add_exp_{character.id}',
            'Повысить уровень': f'incr_level_{character.id}',
            'Изменить': f'change_character_{character.id}',
            'Удалить': f'delete_character_{character.id}'}
    reply_markup = get_callback_buttons(btns=btns, sizes=(2, 2, 2))

    return media, caption, reply_markup
