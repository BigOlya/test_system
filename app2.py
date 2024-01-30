from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__, template_folder = 'C:/Users/79192/Desktop/app2/templates/')
app.secret_key = 'your_secret_key'

# Создаем базу данных SQLite и таблицы для пользователей и проектов
conn = sqlite3.connect('testing2.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   password TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS projects
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   description TEXT,
                   user_id INTEGER,
                   FOREIGN KEY(user_id) REFERENCES users(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS list2
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                project_name TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id));''')
cursor.execute ( '''CREATE TABLE IF NOT EXISTS environments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL)''')
conn.commit()

# Главная страница приложения
@app.route('/')
def index():
    # Проверяем, вошел ли пользователь в систему
    if 'user_id' in session:
        user_id = session['user_id']
        # Получаем список проектов текущего пользователя из базы данных
        cursor.execute("SELECT * FROM projects WHERE user_id=?", (user_id,))
        projects = cursor.fetchall()
        return render_template('projects.html', projects=projects)
    return redirect('/login')

# Страница регистрации нового пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Хешируем пароль пользователя
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Добавляем нового пользователя в базу данных
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return redirect('/login')
    return render_template('register.html')

# Страница входа в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Хешируем введенный пароль
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Проверяем, есть ли пользователь с таким именем и паролем в базе данных
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = cursor.fetchone()
        if user:
            # Если пользователь существует, сохраняем его идентификатор в сессии
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return redirect('/login')
    return render_template('login.html')

# Страница для добавления нового проекта
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    # Проверяем, вошел ли пользователь в систему
    if 'user_id' in session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            user_id = session['user_id']
            # Добавляем новый проект в базу данных, связываем его с текущим пользователем
            cursor.execute("INSERT INTO projects (name, description, user_id) VALUES (?, ?, ?)", (name, description, user_id))
            conn.commit()
            return redirect('/projects')
        return render_template('add_project.html')
    return redirect('/login')

# Удаление элемента
@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    cursor.execute('DELETE FROM  projects WHERE id = ?', (project_id,))
    conn.commit()
    return redirect('/projects')


# Страница выхода из системы
@app.route("/logout")
def logout():
    session.clear()
    return render_template('/logout.html')


@app.route("/main")
def test_plan():
    return render_template("main.html")

@app.route("/projects")
def test_scenarios():
    if 'user_id' in session:
        user_id = session['user_id']
        # Получаем список проектов текущего пользователя из базы данных
        cursor.execute("SELECT * FROM projects WHERE user_id=?", (user_id,))
        projects = cursor.fetchall()
        return render_template('projects.html', projects=projects)
    return redirect('/login')




@app.route("/case")
def case():
         # Получаем список кейсов
        cursor.execute("SELECT * FROM list2")
        case = cursor.fetchall()
        return render_template('case.html', case=case)

# Страница для добавления нового кейса
@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    # Проверяем, вошел ли пользователь в систему
    if 'user_id' in session:
        if request.method == 'POST':
            project = request.form['project_name']
            name = request.form['test_case_name']
            description = request.form['test_case_description']
            # Добавляем новый проект в базу данных, связываем его с текущим пользователем
            cursor.execute("INSERT INTO check_list (name, description, project_name) VALUES (?, ?, ?)", (name, description, project))
            conn.commit()
            return redirect('/case')
        return render_template('add_case.html')
    return redirect('/login') 

# Страница редактирования элемента
@app.route('/edit_case/<int:case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    if request.method == 'POST':
        project = request.form['project_name']
        name = request.form['test_case_name']
        description = request.form['test_case_description']
        cursor.execute('UPDATE  list2 SET name = ?,  description = ?, project_name = ? WHERE id = ?', (name, description, project, case_id))
        conn.commit()
        return redirect('/case')
    cursor.execute('SELECT * FROM  list2 WHERE id = ?', (case_id,))
    case = cursor.fetchone()
    return render_template('edit_case.html', case=case)

# Удаление элемента
@app.route('/delete_case/<int:case_id>')
def delete_case(case_id):
    cursor.execute('DELETE FROM  list2 WHERE id = ?', (case_id,))
    conn.commit()
    return redirect('/case')


@app.route("/for_qa")
def contacts():
    return render_template("for_qa.html")


# Главная страница, отображение элементов из базы данных
@app.route('/environments')
def environments():
    cursor.execute('SELECT * FROM  environments')
    items = cursor.fetchall()
    return render_template('environments.html', items=items)

# Страница создания элемента
@app.route('/add_environment', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute('INSERT INTO  environments (name) VALUES (?)', (name,))
        conn.commit()
        return redirect('/environments')
    return render_template('add_environment.html')

# Страница редактирования элемента
@app.route('/edit_environment/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute('UPDATE  environments SET name = ? WHERE id = ?', (name, item_id))
        conn.commit()
        return redirect('/environments')
    cursor.execute('SELECT * FROM  environments WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    return render_template('edit_environment.html', item=item)

# Удаление элемента
@app.route('/delete/<int:item_id>')
def delete(item_id):
    cursor.execute('DELETE FROM  environments WHERE id = ?', (item_id,))
    conn.commit()
    return redirect('/environments')





if __name__ == '__main__':
    app.run(debug=True)