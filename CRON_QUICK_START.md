# Быстрый старт cron для antibl

## 1. Настройка (один раз)

```bash
# Сделать скрипты исполняемыми
chmod +x run_antibl.sh setup_cron.sh

# Запустить автоматическую настройку cron
./setup_cron.sh
```

## 2. Проверка работы

```bash
# Тестовый запуск
./run_antibl.sh

# Проверка логов
ls -la logs/
tail -f logs/antibl_$(ls -t logs/ | head -1)
```

## 3. Мониторинг

```bash
# Проверка cron задач
crontab -l

# Проверка результатов
wc -l routes.txt
ls -la routes.txt
```

## 4. Удаление cron задачи

```bash
crontab -e
# Удалить строку с run_antibl.sh
```

---

**Default:** runs every hour at 00 minutes

**Logs:** output to stdout (can be redirected in cron)

**Details:** see `CRON_README.md`
