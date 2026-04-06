# LUPA 🔍
**Logistical Utility for Perfect Administration**

LUPA — це веб-додаток для динамічного балансування логістичних ресурсів в умовах стрімкої зміни попиту. Система відмовляється від жорстких статичних маршрутів на користь математичної пріоритизації та жадібних алгоритмів (Greedy algorithm), забезпечуючи автоматичний перерозподіл автопарку в реальному часі.

## Встановлення та локальний запуск

### 1. Клонування репозиторію
```bash
git clone [https://github.com/romart008/hack--test](https://github.com/romart008/hack--test)
cd hack--test
```
### 2. Встановлення залежностей
Переконайтеся, що у вас встановлено Python 3.8+. Встановіть необхідні бібліотеки (Flask):

```bash
pip install flask
```

### 3. Запуск сервера
Запустіть головний файл додатку:

```bash
python app.py
```
Додаток буде доступний у браузері за адресою: http://127.0.0.1:5000/


## Структура проєкту
* app.py — основний файл з логікою Flask та класом LogisticsSystem.
* database/main.db — БД SQLite.
* templates/ — HTML шаблони (home, manager, point, point-log).

## Розробка
Ви можете змінювати базові константи в класі LogisticsSystem:
* self.truck_capacity (за замовчуванням 20)
* self.total_drivers (за замовчуванням 100)
* self.warehouse_capacity (за замовчуванням 1000)
