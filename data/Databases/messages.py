SUPPORTED_LANGUAGES = ['EN', 'RU', 'PL']

PHRASES = {'EN': {0: 'Let\'s start!',
                  1: 'Access denied. Enter your password.',
                  2: 'There are some files missing from your folder on the server. Select any of the categories and the bot will automatically create the necessary files.',
                  3: 'You are in the category "Settings"',
                  4: 'You are in the category "Costs"',
                  5: 'You are in the category "Diet"',
                  6: 'You are in the category "To-do"',
                  7: 'If this is the first time you have met me, you are encouraged to read this guide:',
                  8: 'Here is the guide I was able to find on this section:',
                  9: 'If this information is not enough, press the button below.',
                  10: 'I was unable to find a guide specifically on this section, but you can read these full guide:',
                  11: 'Show settings',
                  12: '. Choose a section. (current settings section is "{}")',
                  13: '. Read the user guide to find out how to keep your costs history.',
                  14: '. Read the user guide to find out how to set up your diet.',
                  15: '. Read the user guide to find out how to use the case assistant.',
                  16: ', section "{}". Read the user guide to find out how to change settings.',
                  17: 'Current {} settings:',
                  18: 'Empty config. Most likely the functionality has not yet been added.',
                  19: 'You are not currently receiving any statistics because the show_report and show_pie options are disabled in the settings. Define in the settings what information you want to receive.',
                  20: 'You don\'t have any statistics at the moment. Add some costs at first.',
                  21: 'Expenses for the period\n',
                  22: 'Oops... these costs could not be processed:',
                  23: 'Like clockwork! Anything else?',
                  24: 'Current list of products allowed in the diet:',
                  25: 'Allowed products are not defined.',
                  26: 'Current list of products required at each meal:',
                  27: 'Required at each meal products are not defined.',
                  28: 'You are in the category "Diet", module "Products". Choose an action.',
                  29: 'Modify allowed products',
                  30: 'Modify each-meal products',
                  31: 'Show current products list',
                  32: 'The functionality of this module has not yet been added.',
                  33: 'Show current {} products list',
                  34: ' and modifying {} products list.',
                  35: 'Sounds like',
                  36: 'Some products are not in the database, but this is what I was able to find:\n\n',
                  37: 'The products have been successfully added! Anything else?',
                  38: 'Your password for the bot is',
                  39: 'Save it and do not show it to anyone, you will need it in case the bot is restarted.',
                  40: 'Weekly stats!',
                  41: 'Monthly stats!',
                  42: 'Good morning!',
                  43: 'Selected {} language.',
                  44: 'The list of allowed products has been cleared',
                  45: 'The list of products required at each meal has been cleared',
                  46: 'Get full user guide'},

           'RU': {0: 'Начнём!',
                  1: 'Доступ запрещён. Введите Ваш пароль.',
                  2: 'В вашей папке на сервере отсутствуют некоторые файлы. Выберите любую из категорий и бот автоматически создаст необходимые файлы.',
                  3: 'Вы находитесь в разделе "Настройки"',
                  4: 'Вы находитесь в разделе "Расходы"',
                  5: 'Вы находитесь в разделе "Питание"',
                  6: 'Вы находитесь в разделе "Дела"',
                  7: 'Если это Ваше первое знакомство со мной, вам рекомендуется прочитать это руководство:',
                  8: 'Вот руководство по этому разделу, которое мне удалось найти:',
                  9: 'Если этой информации недостаточно - нажмите кнопку ниже.',
                  10: 'Мне не удалось найти руководство конкретно по этому разделу, но вы можете прочесть полное руководство ниже:',
                  11: 'Показать настройки',
                  12: '. Выберите категорию настроек. (Текущая категория настроек - "{}")',
                  13: '. Прочитайте руководство пользователя (гайд), чтобы узнать, как вести историю своих расходов.',
                  14: '. Прочитайте руководство пользователя (гайд), чтобы узнать, как настроить свою диету.',
                  15: '. Прочитайте руководство пользователя (гайд), чтобы узнать, как пользоваться помощником по делам.',
                  16: ', категория "{}". Прочитайте руководство пользователя (гайд), чтобы узнать, как изменять настройки.',
                  17: 'Текущие настройки в категории "{}"',
                  18: 'Пустой файл настроек. Вероятнее всего, функционал еще не добавлен.',
                  19: 'На данный момент вы не получаете никакой статистики, поскольку в настройках отключены параметры show_report и show_pie. Определите в настройках, какую информацию вы хотите получать.',
                  20: 'Статистика отсутствует. Для начала добавьте какие-нибудь расходы.',
                  21: 'Расходы за период\n',
                  22: 'Упс... эти расходы обработать не удалось:',
                  23: 'Как по маслу! Что-нибудь ещё?',
                  24: 'Текущий список продуктов, допустимых в рационе:',
                  25: 'Допустимые продукты не определены.',
                  26: 'Текущий список продуктов, обязательных в каждом приеме пищи:',
                  27: 'Продукты, обязательные в каждом приеме пищи не определены.',
                  28: 'Вы находитесь в разделе "Питание", категория "Продукты". Выберите действие.',
                  29: 'Редактировать допустимые продукты',
                  30: 'Редактировать обязательные продукты',
                  31: 'Показать текущий список продуктов',
                  32: 'Функционал еще не добавлен.',
                  33: 'Текущий список {} продуктов',
                  34: ' в режиме редактирования списка {} продуктов.',
                  35: 'Похоже на',
                  36: 'Некоторые продукты отсутствуют в базе данных, но вот, что мне удалось найти:\n\n',
                  37: 'Продукты успешно добавлены! Что-нибудь ещё?',
                  38: 'Вот Ваш пароль к боту:',
                  39: 'Сохраните его и никому не показывайте, он понадобится Вам, если бот перезапустится.',
                  40: 'Еженедельная статистика!',
                  41: 'Ежемесячная статистика!',
                  42: 'Доброе утро!',
                  43: 'Установлен {} язык.',
                  44: 'Список допустимых продуктов успешно очищен.',
                  45: 'Список обязательных продуктов успешно очищен.',
                  46: 'Читать полное руководство'},

           'PL': {0: 'Do roboty!!',
                  1: 'Odmowa dostępu. Proszę wprowadzić hasło.',
                  2: 'W Twoim folderze na serwerze brakuje kilku plików. Przejdź do dowolnego działu i bot automatycznie utworzy potrzebne pliki.',
                  3: 'Jesteś w dziale "Ustawienia"',
                  4: 'Jesteś w dziale "Wydatki"',
                  5: 'Jesteś w dziale "Dieta"',
                  6: 'Jesteś w dziale "Sprawy"',
                  7: 'Jeśli masz do czynienia ze mną po raz pierwszy, sugeruję przeczytać instrukcję obsługi (guide):',
                  8: 'Oto guide, dotyczący tego działu, kóry potrafiłem znaleźć:',
                  9: 'Gdyby ta informacja nie była wystarczająca, proszę nacisnąć przycisk niżej.',
                  10: 'Niestety, nie udało mi się znaleźć instrukcji obsługi, dotyczącej konkretnie tego działu, ale zawsze możesz przeczytać pełną instrukcję:',
                  11: 'Wyświetl ustawienia',
                  12: '. Wybierz kategorię ustawień. (Aktualna kategoria ustawień to "{}")',
                  13: '. Przeczytaj instrukcję obsługi (guide), żeby dowiedzieć się jak zarządzać historią swoich wydatków.',
                  14: '. Przeczytaj instrukcję obsługi (guide), żeby dowiedzieć się jak zarządzać swoją dietą.',
                  15: '. Przeczytaj instrukcję obsługi (guide), żeby dowiedzieć się jak korzystać z pomocy asystenta spraw.',
                  16: ', kategoria "{}". Przeczytaj instrukcję obsługi (guide), żeby dowiedzieć się jak edytować ustawienia.',
                  17: 'Aktualne ustawienia w kategorii "{}"',
                  18: 'Pusty plik ustawień. Najprawdopodobniej, bot jeszcze nie posiada tej funkcjonalności.',
                  19: 'Na razie nie otrzymujesz żadnej statystyki, gdyż w ustawieniach parametry show_report oraz show_pie są ustawione jako False. Edytuj w ustawieniach informację którą chcesz odbierać.',
                  20: 'Brak statystyki. Najpierw wprowadź jakieś wydatki.',
                  21: 'Wydatki za okres\n',
                  22: 'Ups... te wydatki nie mogą zostać przetworzone:',
                  23: 'Jak nóż w masło! Coś jeszcze?',
                  24: 'Aktualna lista produktów, dopuszczalnych w diecie:',
                  25: 'Dopuszczalne produkty nie są zdefiniowane.',
                  26: 'Aktualna lista produktów, obowiązujących w każdym posiłku:',
                  27: 'Produkty, obowiązujące w każdym posiłku nie są zdefiniowane.',
                  28: 'Jesteś w dziale "Dieta", kategoria "Produkty". Wybierz co chcesz zrobić.',
                  29: 'Edytować dopuszczalne podukty',
                  30: 'Edytować obowiązkowe produkty',
                  31: 'Wyświetl aktualną listę produktów',
                  32: 'Bot jeszcze nie posiada tej funkcjonalności.',
                  33: 'Aktualna lista {} produktów',
                  34: ' w trybie edytowania listy {} produktów.',
                  35: 'Brzmi jak',
                  36: 'Niektórych produktów nie ma w mojej bazie, ale byłem w stanie znaleźć to:\n\n',
                  37: 'Produkty dodane! Coś jeszcze?',
                  38: 'To jest Twoje hasło do bota:',
                  39: 'Zachowaj go i nikomu nie udostępniaj, będziesz go potrzebował w przypadku gdy bot zostanie zresetowany.',
                  40: 'Cotygodniowa statystyka!',
                  41: 'Comiesięczna statystyka!',
                  42: 'Dzień dobry!',
                  43: 'Wybrano język {}.',
                  44: 'Lista dopuszczalnych produktów została wyczyszczona.',
                  45: 'Lista obowiązkowych produktów została wyczyszczona.',
                  46: 'Pełna instrukcja obsługi'}
           }

WORDS = {'Settings': {'EN': 'Settings', 'RU': 'Settings', 'PL': 'Settings'},
         'Costs': {'EN': 'Costs', 'RU': 'Расходы', 'PL': 'Wydatki'},
         'Diet': {'EN': 'Diet', 'RU': 'Питание', 'PL': 'Dieta'},
         'To-do': {'EN': 'To-do', 'RU': 'Дела', 'PL': 'Sprawy'},
         'Guide': {'EN': 'Guide', 'RU': 'Гайд', 'PL': 'Guide'},
         'Stats': {'EN': 'Stats', 'RU': 'Статистика', 'PL': 'Statystyka'},
         'Products': {'EN': 'Products', 'RU': 'Продукты', 'PL': 'Produkty'},
         'Generate': {'EN': 'Generate', 'RU': 'Сгенерировать', 'PL': 'Wygeneruj'},
         'Reminder': {'EN': 'Reminder', 'RU': 'Напоминание', 'PL': 'Przypomnienie'},
         'To-do list': {'EN': 'To-do list', 'RU': 'Список дел', 'PL': 'Lista spraw'},
         'General': {'EN': 'General', 'RU': 'Основные', 'PL': 'Główne'},
         '/day': {'EN': '/day', 'RU': '/день', 'PL': '/dzień'},
         '\n\nTotal: ': {'EN': '\n\nTotal: ', 'RU': '\n\nВсего: ', 'PL': '\n\nRazem: '},
         ' per day)': {'EN': ' per day)', 'RU': ' в день)', 'PL': ' dziennie)'},
         'allowed': {'EN': 'allowed', 'RU': 'допустимых', 'PL': 'dopuszczalnych'},
         'each-meal': {'EN': 'each-meal', 'RU': 'обязательных', 'PL': 'obowiązkowych'},
         'EN': {'EN': 'english', 'RU': 'английский', 'PL': 'angielski'},
         'RU': {'EN': 'russian', 'RU': 'русский', 'PL': 'rosyjski'},
         'PL': {'EN': 'polish', 'RU': 'польский', 'PL': 'polski'},
         'Other': {'EN': 'Other', 'RU': 'Другое', 'PL': 'Inne'}}


def check_messages_file():
    failures = []
    for language in SUPPORTED_LANGUAGES:
        if language not in PHRASES.keys():
            failures.append(f'{language} есть в SUPPORTED_LANGUAGES но отсутствует в PHRASES.')
        else:
            if PHRASES[language].keys() != PHRASES[list(PHRASES.keys())[0]].keys():
                failures.append(
                    f'Различные индексы фраз (или их кол-во) для языков {language} и {SUPPORTED_LANGUAGES[0]}.')
        if language not in WORDS.keys():
            failures.append(f'{language} есть в SUPPORTED_LANGUAGES но отсутствует в WORDS.')
        for word in WORDS:
            if language not in WORDS[word].keys():
                failures.append(f'В словаре WORDS для слова {word} не определен перевод для языка {language}.')

    if failures:
        for i in range(len(failures)):
            failures[i] = failures[i].replace('\n', '\\n')
        raise ValueError('Тест языкового пакета провален:\n\n' + '\n'.join(failures))
    else:
        print('Тест языкового пакета успешно пройден')


check_messages_file()
