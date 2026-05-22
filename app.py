from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = 'entries.json'

# --- Задание 12. Функции работы с JSON ---
def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_entries(entries_list):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries_list, f, ensure_ascii=False, indent=4)

# Загрузка записей в глобальную переменную entries
entries = load_entries()

# --- Задание 13. Маршрут главной страницы ---
@app.route('/')
def index():
    global entries
    entries = load_entries()
    return render_template('index.html', entries=entries)

# --- Задание 14. Маршрут просмотра записи ---
@app.route('/entry/<int:entry_id>')
def detail(entry_id):
    global entries
    entries = load_entries()
    entry = next((e for e in entries if e.get('id') == entry_id), None)
    if entry:
        return render_template('detail.html', entry=entry)
    else:
        return "Запись не найдена", 404

# --- Задание 15. Маршрут добавления записи ---
@app.route('/add', methods=['GET', 'POST'])
def add():
    global entries
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        entries = load_entries()
        new_id = max([e.get('id', 0) for e in entries], default=0) + 1
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        new_entry = {
            "id": new_id,
            "title": title,
            "content": content,
            "date": current_date
        }
        
        entries.append(new_entry)
        save_entries(entries)
        return redirect(url_for('index'))
        
    return render_template('add.html')

# --- Задание 16. Маршрут редактирования записи ---
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    global entries
    entries = load_entries()
    entry = next((e for e in entries if e.get('id') == entry_id), None)
    
    if not entry:
        return "Запись не найдена", 404
        
    if request.method == 'POST':
        entry['title'] = request.form.get('title')
        entry['content'] = request.form.get('content')
        save_entries(entries)
        return redirect(url_for('index'))
        
    return render_template('edit.html', entry=entry)

# --- Задание 17. Маршрут удаления записи ---
@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    global entries
    entries = load_entries()
    entries = [e for e in entries if e.get('id') != entry_id]
    save_entries(entries)
    return redirect(url_for('index'))

# --- Задание 18. Маршрут поиска ---
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip().lower()
    all_entries = load_entries()
    # Фильтруем: ищем вхождение строки в заголовке без учёта регистра
    filtered_entries = [e for e in all_entries if query in e.get('title', '').lower()]
    return render_template('index.html', entries=filtered_entries)

# --- Задание 19. Маршрут фильтра по дате ---
@app.route('/filter/week', methods=['GET'])
def filter_week():
    all_entries = load_entries()
    filtered_entries = []
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    
    for e in all_entries:
        date_str = e.get('date', '')
        try:
            # Преобразуем строку даты обратно в объект datetime для сравнения
            entry_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            if seven_days_ago <= entry_date <= now:
                filtered_entries.append(e)
        except ValueError:
            # Если формат даты почему-то не совпал, пропускаем запись
            continue
            
    return render_template('index.html', entries=filtered_entries)

# --- Задание 20. Запуск приложения ---
if __name__ == '__main__':
    app.run(debug=True)