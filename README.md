# ![MiCreate48x48](https://raw.githubusercontent.com/ooflet/Mi-Create/main/src/resources/MiCreate48x48.png)
### Mi Create
Unofficial watchface and application creator for Xiaomi Wearables.

Compatible with all Xiaomi wearables made ~2021 and above (Devices manufactured by 70mai & Longcheer)

### 🇬🇧 EN
### Features:
- Intuitive and elegant user interface
- Easy to build & unpack watch faces
- Powerful integrated text editor
- Language support

### Installation:
Download the latest installer from the [releases](https://github.com/ooflet/Mi-Create/releases) tab.

### Running source code
If there are no prebuilt packages for your OS, you may opt to run directly from source:
- Clone repo
- Install Python version >3.8 & install dependencies through pip: PyQt6, PyQt6-QScintilla, xmltodict, nuitka
- Execute main.py

Executing from source however will not create log files, it will output logs to console.

If you would like to build a package for your platform, use Nuitka as there are some Nuitka-specific checks (specifically the `__compiled__` global check in main.py:36).

### Licensing:
Mi Create is licensed under the GPL-3 licence. [View what you can and can't do](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)   
Please note that the compiler & decompiler is made by a third party and is **NOT** open source.

### 🇷🇺 RU

### Функции:
- Интуитивно понятный и элегантный пользовательский интерфейс
- Легко создавать и распаковывать циферблаты
- Мощный интегрированный текстовый редактор.
- Языковая поддержка

### Монтаж:
Загрузите последнюю версию установщика со вкладки [релизы](https://github.com/ooflet/Mi-Create/releases).

### Запуск исходного кода
Если для вашей ОС нет готовых пакетов, вы можете запустить непосредственно из исходного кода:
- Репозиторий клонов
- Установите Python версии > 3.8 и установите зависимости через pip: PyQt6, PyQt6-QScintilla, xmltodict, nuitka.
- Выполните main.py

Однако выполнение из исходного кода не создает файлы журналов, а выводит журналы на консоль.

Если вы хотите собрать пакет для своей платформы, используйте Nuitka, поскольку существуют некоторые проверки, специфичные для Nuitka (в частности, глобальная проверка `__compiled__` в main.py:36).

### Лицензирование:
Mi Create распространяется по лицензии GPL-3. [Просмотрите, что вы можете и чего не можете делать](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60)
Обратите внимание, что компилятор и декомпилятор созданы третьей стороной и **НЕ** имеют открытый исходный код.