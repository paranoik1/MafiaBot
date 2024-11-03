GITHUB_URL = "https://github.com/paranoik1"


HELP_FIELDS = {
    "Общая информация": """
- **/help** - инструкция по использованию бота
- **/author** - информация об авторе бота
- **/game** - информация об игре Мафия
- **/roles** - роли в игре
""",
    "Подписка и покупки": """
- **/subscription** - информация о платной подписке
- **/buy** - приобрести платную подписку 
""",
    "Управление игрой": """
- **/start-mafia** - начать игру в Мафию
- **/voting** - проведение голосования
- **/night** - ночная фаза игры
- **/stop-mafia** - завершение игры 
"""
}

AUTHOR_NAME = "paranoik"
AUTHOR_TEXT = f"""
Меня создал **{AUTHOR_NAME}** - Python разработчик и большой любитель игры **"Мафия"**. 

Вы можете ознакомиться с другими проектами **{AUTHOR_NAME}** на его [GitHub]({GITHUB_URL}).

Также приглашаем вас воспользоваться хостинговым сервером нашего друга, на котором работает бот для игры в "Мафию".
Связаться можете с ним по [Telegram](https://t.me/gamplez) или по [GitHub](https://github.com/JohnMazino).
"""


GAME_TEXT = """
Мафия - это классическая социальная ролевая игра, в которой группа игроков пытается вычислить и "казнить" членов вражеской команды. В боте присутствует большое количество различных ролей, с которыми вы можете ознакомиться в команде **/roles**.

Каждый игрок получает определенную роль - мирный житель, мафиози, детектив и т.д. - и должен действовать в соответствии с ней. 
Одной из таких особых ролей является маньяк - одиночный игрок, целью которого является истребить всех других и остаться в игре единственным выжившим.

Целью игры является либо уничтожить всех мафиози, либо, наоборот, дать им победить. Сложность в том, что настоящие мафиози скрывают свою личину, пытаясь ввести других игроров в заблуждение.

Игра состоит из нескольких фаз:
- Ночь - мафиози и другие ролевые персонажи действуют
- День - игроки обсуждают и пытаются выявить мафиози
- Голосование - игроки голосуют за тех, кого считают виновными

Победа достается либо мирным жителям, либо мафии/одиночке - в зависимости от того, кто останется в живых к концу игры.
"""


SUBSCRIPTION_TEXT = """
Платная версия нашего Мафия-бота дает вам ряд дополнительных возможностей и преимуществ:

- Будет увеличен максимальный лимит игроков в партиях - c 12 до 25 человек. Это позволит проводить более масштабные и интересные игры.

- Будут доступны дополнительные уникальные роли, включая редкие и специальные. Это добавит больше разнообразия и интриги в ваши игры.

- Будут доступны эксклюзивные команды и специальные возможности, недоступные в бесплатной версии.

- Будут доступны настройки игры: вы сможете настраивать роли в игре, выбирать различные режимы игры, менять кол-во игроков и многое другое

- Вы получите возможность играть в Мафию без ведущего. Бот будет самостоятельно проводить игру, озвучивая все события в голосовом чате. Это добавит новый уровень погружения и удобства в ваши партии.

Стоимость подписки составляет **{}** рублей в месяц.
Приобрести ее можно по команде **/buy**.
"""

BUY_TEXT = """
Мы рады представить вам премиум-версию нашего бота по мафии для Discord! Эта версия предлагает расширенный функционал, который сделает ваши игры еще более захватывающими и увлекательными.

Вы можете приобрести премиум-версию для себя лично или для целого сервера:

Личная премиум-версия:
- Премиум-функции доступны только для вас
- Отличный выбор для индивидуальной игры или небольших групп
**Стоимость:** {user_price} рублей

Премиум-версия для сервера:
- Премиум-функции доступны для всех участников сервера
- Идеальное решение для крупных игровых сообществ
**Стоимость:** {guild_price} рублей
"""

PAYMENT_SUCCESS_TEXT = """
Поздравляем!

Вы успешно приобрели премиум-версию нашего бота по мафии для Discord. Теперь вы можете в полной мере наслаждаться всеми преимуществами премиум-функций.

Если у вас возникнут какие-либо вопросы или проблемы, пожалуйста, не стесняйтесь обращаться в нашу службу поддержки. Мы всегда готовы помочь вам.

Спасибо за выбор нашего премиум-бота по мафии! Желаем вам увлекательных и захватывающих игр!
"""

INSTRUCTION_BUY_TEXT = """
Чтобы приобрести премиум-версию, нажмите на кнопку "Оплатить" ниже. Вы будете перенаправлены на безопасную платежную страницу YooMoney, где сможете совершить оплату. 
После успешной оплаты нажмие на кнопку "Проверить", чтобы бот подтвердил ваш платеж. 
И по итогу вы сможете использовать все премиум-возможности бота после завершения всех этих шагов.
"""


SETTINGS_FIELDS = {
    "**Кол-во игроков**": "При нажатии на эту кнопку откроется модальное окно, в котором вы сможете установить минимальное и максимальное количество игроков, которые могут участвовать в вашей игре. Это позволит вам настроить оптимальный размер игровой группы.",
    "**Роли в игре**": "Эта кнопка открывает окно, в котором вы можете управлять ролями, доступными в вашей игре. Вы сможете включать или отключать различные роли, такие как Мафия, Комиссар, Доктор и другие. Это дает вам возможность настраивать игровой процесс под ваши предпочтения.",
    "**Смена режима игры**": "Нажав на эту кнопку, вы сможете переключаться между 'Автоматическим' и 'Модераторским' режимами игры. В 'Автоматическом' режиме игра будет полностью автоматизирована, а в 'Модераторском' режиме вам придется вручную управлять некоторыми аспектами игрового процесса.",
    "**Режим раскрытия ролей**": "Эта кнопка позволяет вам выбирать, будут ли роли игроков раскрываться после их выбывания из игры. В 'Анонимном' режиме роли останутся скрытыми, а в 'Публичном' режиме они будут раскрываться для всех участников. Это дает вам возможность настраивать уровень открытости и неопределенности в игре.",
    "**Голосовое сопровождение**": "Включение этой функции добавит в игру голосовые комментарии и озвучивание ключевых событий. Это поможет создать более атмосферную и погружающую игровую среду для участников."
}

DESCRIPTION_VOTING = "Проголосуйте за игрока, которого считаете убийцей"