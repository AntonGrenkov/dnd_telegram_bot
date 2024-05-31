from random import randint

stats_list = ('strength',
              'dexterity',
              'constitution',
              'intelligence',
              'wisdom',
              'charisma',
              # для перехода в другую фазу
              'stats_finish')


def get_stats_auto_result():

    caption = ('Результаты бросков:\n'
               '----------------------\n')
    result_list = []
    for a in range(1, 7):

        roll = []
        for _ in range(4):
            roll.append(randint(1, 6))
        roll_raw = tuple(sorted(roll))

        roll_result = roll_raw[1:]
        res_sum = sum(roll_result)
        result_list.append(res_sum)

        caption += f'{tuple(roll)} -> '
        for index, dice in enumerate(roll_result):
            if index < len(roll_result) - 1:
                caption += f'<strong>{dice}</strong>+'
            else:
                caption += f'<strong>{dice}</strong>'
        caption += f'=<strong>{res_sum}</strong>\n'

    stats = tuple(sorted(result_list, reverse=True))
    caption += (
        f'----------------------\n'
        f'{(", ".join(map(str, stats)))}'
    )

    return stats, caption
