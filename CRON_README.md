# Настройка cron для antibl

Этот документ описывает, как настроить автоматический запуск antibl через cron для регулярного обновления списка заблокированных маршрутов.

## Файлы

- `run_antibl.sh` - основной скрипт для запуска antibl
- `setup_cron.sh` - скрипт для автоматической настройки cron задачи
- `CRON_README.md` - этот файл с инструкциями

## Quick Setup

1. **Ensure virtual environment is created and dependencies are installed:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the cron setup script:**
   ```bash
   ./setup_cron.sh
   ```

3. **The script will:**
   - Check for all necessary files
   - Provide manual cron setup instructions
   - Give alternative setup options for macOS
   - Provide usage instructions

## Ручная настройка cron

Если вы предпочитаете настроить cron вручную:

1. **Откройте crontab для редактирования:**
   ```bash
   crontab -e
   ```

2. **Добавьте строку (замените путь на ваш):**
   ```bash
   # Запуск antibl каждый час
   0 * * * * /полный/путь/к/antibl/run_antibl.sh
   ```

3. **Сохраните и выйдите из редактора**

## Расписание cron

По умолчанию скрипт настроен на запуск **каждый час** в 00 минут.

Другие варианты расписания:

```bash
# Каждые 30 минут
*/30 * * * * /путь/к/run_antibl.sh

# Каждые 2 часа
0 */2 * * * /путь/к/run_antibl.sh

# Каждый день в 3:00 утра
0 3 * * * /путь/к/run_antibl.sh

# Каждые 6 часов
0 */6 * * * /путь/к/run_antibl.sh
```

## Тестирование

**Перед настройкой cron обязательно протестируйте скрипт:**

```bash
./run_antibl.sh
```

**Check:**
- Is `routes.txt` file created
- Are there any errors in output
- Does the script complete successfully

## Logging

The script outputs all information to stdout (standard output). When running via cron, this output will be sent to the system's cron log or email (depending on your system configuration).

**To capture output in cron, you can redirect it:**
```bash
# Redirect to a log file
0 * * * * /path/to/run_antibl.sh > /path/to/antibl.log 2>&1

# Send output via email (if mail is configured)
0 * * * * /path/to/run_antibl.sh | mail -s "antibl output" your@email.com
```

## Мониторинг

**Проверка работы cron:**
```bash
# Просмотр текущих cron задач
crontab -l

# Проверка логов cron (если доступно)
sudo tail -f /var/log/cron
sudo tail -f /var/log/syslog | grep CRON
```

**Check results:**
```bash
# routes.txt file size
wc -l routes.txt

# Last modification time
ls -la routes.txt

# Last few lines content
tail -5 routes.txt
```

## Устранение неполадок

### Проблема: Скрипт не выполняется по cron

**Возможные причины:**
1. **Путь к скрипту неверный** - используйте абсолютный путь
2. **Скрипт не исполняемый** - выполните `chmod +x run_antibl.sh`
3. **Проблемы с правами** - проверьте права на файлы и директории
4. **Виртуальное окружение недоступно** - убедитесь, что venv существует

**Решение:**
```bash
# Проверьте права
ls -la run_antibl.sh

# Сделайте исполняемым
chmod +x run_antibl.sh

# Проверьте путь в cron
crontab -l

# Протестируйте вручную
./run_antibl.sh
```

### Проблема: Ошибки в логах

**Проверьте:**
1. **Зависимости установлены** - `pip list` в виртуальном окружении
2. **Интернет доступен** - для загрузки данных
3. **Диски не заполнены** - `df -h`
4. **Права на запись** - в текущую директорию

### Проблема: Cron не работает в macOS

**В macOS cron может быть отключен. Включите:**
```bash
# Проверьте статус
sudo launchctl list | grep cron

# Включите cron
sudo launchctl load -w /System/Library/LaunchDaemons/com.vix.cron.plist
```

## Удаление cron задачи

**Автоматически:**
```bash
crontab -e
# Удалите строку с run_antibl.sh
```

**Или полностью очистите crontab:**
```bash
crontab -r
```

## Безопасность

- **Не запускайте скрипт от root** без необходимости
- **Проверяйте права** на файлы и директории
- **Мониторьте логи** на предмет подозрительной активности
- **Регулярно обновляйте** зависимости Python

## Поддержка

При возникновении проблем:
1. Проверьте логи в директории `logs/`
2. Протестируйте скрипт вручную
3. Проверьте настройки cron
4. Убедитесь, что все зависимости установлены
