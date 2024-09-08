from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Datos de autenticación del administrador
ADMIN_USERNAME = 'intesud'
ADMIN_PASSWORD = '123'

# Decorador para proteger las rutas de administración
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='instituto_sga_bd'
    )
    return connection

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error en el registro: {err}')
            conn.rollback()
        finally:
            conn.close()
        
    return render_template('registro.html')  # Asegúrate de que este template existe



@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Autenticación de Administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username  # Opcional: Guardar el nombre de usuario en la sesión
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas.')
            return redirect(url_for('login'))
    
    return render_template('index.html')
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Sesión cerrada.')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# Gestión de Usuarios
@app.route('/admin/users')
@login_required
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        conn.commit()
        conn.close()
        
        flash('Usuario creado exitosamente.')
        return redirect(url_for('list_users'))
    
    return render_template('admin/user_form.html')

@app.route('/admin/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute('UPDATE users SET username = %s, password = %s WHERE id = %s', (username, password, id))
        conn.commit()
        conn.close()
        
        flash('Usuario actualizado exitosamente.')
        return redirect(url_for('list_users'))
    
    conn.close()
    return render_template('admin/user_form.html', user=user)

@app.route('/admin/user/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    
    flash('Usuario eliminado exitosamente.')
    return redirect(url_for('list_users'))

# Gestión de Estudiantes
@app.route('/students')
@login_required
def list_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return render_template('student.html', students=students)

@app.route('/student/new', methods=['GET', 'POST'])
def new_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (name, email) VALUES (%s, %s)', (name, email))
        conn.commit()
        conn.close()
        
        flash('Estudiante creado exitosamente.')
        return redirect(url_for('list_students'))
    
    return render_template('student_form.html')  # Asegúrate de que este archivo exista y esté configurado


@app.route('/student/<int:id>/edit', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
    student = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        cursor.execute('UPDATE students SET name = %s, email = %s WHERE id = %s', (name, email, id))
        conn.commit()
        conn.close()
        
        flash('Estudiante actualizado exitosamente.')
        return redirect(url_for('list_students'))
    
    conn.close()
    return render_template('student_form.html', student=student)

@app.route('/student/<int:id>/delete', methods=['POST'])
@login_required
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    
    flash('Estudiante eliminado exitosamente.')
    return redirect(url_for('list_students'))

# Gestión de Profesores
@app.route('/professors')
@login_required
def list_professors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM professors')
    professors = cursor.fetchall()
    conn.close()
    return render_template('professor.html', professors=professors)

@app.route('/professor/new', methods=['GET', 'POST'])
def new_professor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO professors (name, email) VALUES (%s, %s)', (name, email))
        conn.commit()
        conn.close()
        
        flash('Profesor creado exitosamente.')
        return redirect(url_for('list_professors'))
    
    return render_template('professor_form.html')

@app.route('/professor/<int:id>/edit', methods=['GET', 'POST'])
def edit_professor(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM professors WHERE id = %s', (id,))
    professor = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        cursor.execute('UPDATE professors SET name = %s, email = %s WHERE id = %s', (name, email, id))
        conn.commit()
        conn.close()
        
        flash('Profesor actualizado exitosamente.')
        return redirect(url_for('list_professors'))
    
    conn.close()
    return render_template('professor_form.html', professor=professor)

@app.route('/professor/<int:id>/delete', methods=['POST'])
def delete_professor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM professors WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    
    flash('Profesor eliminado exitosamente.')
    return redirect(url_for('list_professors'))

# Gestión de Cursos
@app.route('/courses')
@login_required
def list_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT courses.*, professors.name as professor_name FROM courses LEFT JOIN professors ON courses.professor_id = professors.id')
    courses = cursor.fetchall()
    conn.close()
    return render_template('course.html', courses=courses)

@app.route('/course/new', methods=['GET', 'POST'])
def new_course():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM professors')
    professors = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        professor_id = request.form['professor_id']
        
        cursor.execute('INSERT INTO courses (name, description, professor_id) VALUES (%s, %s, %s)', (name, description, professor_id))
        conn.commit()
        conn.close()
        
        flash('Curso creado exitosamente.')
        return redirect(url_for('list_courses'))
    
    conn.close()
    return render_template('course_form.html', professors=professors)

@app.route('/course/<int:id>/edit', methods=['GET', 'POST'])
def edit_course(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM courses WHERE id = %s', (id,))
    course = cursor.fetchone()
    cursor.execute('SELECT * FROM professors')
    professors = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        professor_id = request.form['professor_id']
        
        cursor.execute('UPDATE courses SET name = %s, description = %s, professor_id = %s WHERE id = %s', (name, description, professor_id, id))
        conn.commit()
        conn.close()
        
        flash('Curso actualizado exitosamente.')
        return redirect(url_for('list_courses'))
    
    conn.close()
    return render_template('course_form.html', course=course, professors=professors)

@app.route('/course/<int:id>/delete', methods=['POST'])
@login_required
def delete_course(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM courses WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    
    flash('Curso eliminado exitosamente.')
    return redirect(url_for('list_courses'))

# Gestión de Matrículas
@app.route('/enrollments')
@login_required
def list_enrollments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT enrollments.*, students.name as student_name, courses.name as course_name 
                      FROM enrollments 
                      LEFT JOIN students ON enrollments.student_id = students.id
                      LEFT JOIN courses ON enrollments.course_id = courses.id''')
    enrollments = cursor.fetchall()
    conn.close()
    return render_template('enrollment.html', enrollments=enrollments)

@app.route('/enrollment/new', methods=['GET', 'POST'])
def new_enrollment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    cursor.execute('SELECT * FROM courses')
    courses = cursor.fetchall()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        
        cursor.execute('INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)', (student_id, course_id))
        conn.commit()
        conn.close()
        
        flash('Matrícula realizada exitosamente.')
        return redirect(url_for('list_enrollments'))
    
    conn.close()
    return render_template('enrollment_form.html', students=students, courses=courses)

@app.route('/enrollment/<int:id>/delete', methods=['POST'])
@login_required
def delete_enrollment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM enrollments WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    
    flash('Matrícula eliminada exitosamente.')
    return redirect(url_for('list_enrollments'))

if __name__ == '__main__':
    app.run(debug=True)