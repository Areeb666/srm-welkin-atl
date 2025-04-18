from flask import Flask, request, redirect, render_template, jsonify, url_for
import sqlite3
import os

app = Flask(__name__, template_folder='.') 

# Initialize database
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
   
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_class TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')

    # Create items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Create assignment table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route (show the index.html directly)
@app.route('/')
def home():
    return render_template('index.html')

# Handle form submission for adding students
@app.route('/addstudents')
def addstudents():
    return render_template('addstudents.html', success=False)

@app.route('/submit_student', methods=['POST'])
def submit_student():
    if request.method == 'POST':
        name = request.form['name']
        student_class = request.form['class']
        phone = request.form['phone']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO students (name, student_class, phone) VALUES (?, ?, ?)', (name, student_class, phone))
        conn.commit()
        conn.close()

    return render_template('addstudents.html', success=True)

# Route to view students with search functionality
@app.route('/viewstudents')
def viewstudents():
    search_query = request.args.get('q', '')  # Get the search query from the request

    conn = get_db_connection()
    c = conn.cursor()

    # Search students by name or class
    c.execute("SELECT * FROM students WHERE name LIKE ? OR student_class LIKE ?", ('%' + search_query + '%', '%' + search_query + '%'))
    students = c.fetchall()
    conn.close()

    return render_template('viewstudents.html', students=students, search_query=search_query)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = get_db_connection()
    
    # First delete any assignments for this student
    c = conn.cursor()
    c.execute('DELETE FROM assignments WHERE student_id = ?', (student_id,))
    
    # Then delete the student
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect('/viewstudents')

# Route for adding items
@app.route('/additems', methods=['GET', 'POST'])
def add_items():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (item_name, quantity) VALUES (?, ?)", (item_name, quantity))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Item added successfully'}), 200
    
    return render_template('additems.html')

# Route to view items with search functionality
@app.route('/viewitems')
def view_items():
    search_query = request.args.get('q', '')

    conn = get_db_connection()
    c = conn.cursor()

    # Query to get items with their assigned and available counts
    c.execute("""
        SELECT 
            i.id, 
            i.item_name, 
            i.quantity as total_quantity,
            COUNT(a.id) as assigned,
            i.quantity - COUNT(a.id) as available
        FROM 
            items i
        LEFT JOIN 
            assignments a ON i.id = a.item_id
        WHERE 
            i.item_name LIKE ?
        GROUP BY 
            i.id
    """, ('%' + search_query + '%',))
    
    items = c.fetchall()
    conn.close()

    return render_template('viewitems.html', items=items, search_query=search_query)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = get_db_connection()
    
    # First check if the item is assigned to any student
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM assignments WHERE item_id = ?', (item_id,))
    count = c.fetchone()[0]
    
    if count > 0:
        # Delete assignments first
        c.execute('DELETE FROM assignments WHERE item_id = ?', (item_id,))
    
    # Then delete the item
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_items'))

# Route for assigning items to students
@app.route('/assignitems', methods=['GET', 'POST'])
def assign_items():
    success = False

    if request.method == 'POST':
        student_id = request.form['student']
        item_id = request.form['item']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if there are available items to assign
        cursor.execute("""
            SELECT 
                i.quantity - COUNT(a.id) as available
            FROM 
                items i
            LEFT JOIN 
                assignments a ON i.id = a.item_id
            WHERE 
                i.id = ?
            GROUP BY 
                i.id
        """, (item_id,))
        
        result = cursor.fetchone()
        available = result[0] if result else 0
        
        if available > 0:
            # Insert into assignments table
            cursor.execute("INSERT INTO assignments (student_id, item_id) VALUES (?, ?)", (student_id, item_id))
            conn.commit()
            success = True
        
        conn.close()

        # Fetch all students and items for selection
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM students')
        students = c.fetchall()
        c.execute('SELECT * FROM items')
        items = c.fetchall()
        conn.close()

        return render_template('assignitems.html', students=students, items=items, success=success)

    # Fetch all students and items for selection
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('SELECT * FROM students')
    students = c.fetchall()

    c.execute('SELECT * FROM items')
    items = c.fetchall()

    conn.close()

    return render_template('assignitems.html', students=students, items=items, success=success)

# Route to fix the test URL and redirect to assignitems
@app.route('/test')
def test():
    return redirect('/assignitems')

# New route for viewing assignments
@app.route('/viewassignments')
def view_assignments():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Join query to get assignments with student and item details
    c.execute("""
        SELECT 
            a.id as assignment_id,
            s.id as student_id,
            s.name as student_name,
            s.student_class as student_class,
            i.id as item_id,
            i.item_name as item_name
        FROM 
            assignments a
        JOIN 
            students s ON a.student_id = s.id
        JOIN 
            items i ON a.item_id = i.id
        ORDER BY
            s.name, i.item_name
    """)
    
    assignments = c.fetchall()
    conn.close()
    
    return render_template('viewassignments.html', assignments=assignments)

# Route to unassign/return an item
@app.route('/unassign_item/<int:assignment_id>', methods=['POST'])
def unassign_item(assignment_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
    conn.commit()
    conn.close()
    
    return redirect('/viewassignments')

# Routes for editing items and students
@app.route('/edit_item', methods=['POST'])
def edit_item():
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE items SET item_name = ?, quantity = ? WHERE id = ?", 
                     (item_name, quantity, item_id))
        conn.commit()
        conn.close()
        
        return redirect('/viewitems')

@app.route('/edit_student', methods=['POST'])
def edit_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        student_class = request.form['class']
        phone = request.form['phone']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET name = ?, student_class = ?, phone = ? WHERE id = ?", 
                     (name, student_class, phone, student_id))
        conn.commit()
        conn.close()
        
        return redirect('/viewstudents')

if __name__ == '__main__':
    init_db()
    # Set debug mode based on environment
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode)
