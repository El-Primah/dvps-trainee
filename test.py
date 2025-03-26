from flask import Flask, request, redirect, url_for, render_template
import psycopg2 

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(""" 
        host=rc1a-83kyh7jodfmzqujr.mdb.yandexcloud.net 
        port=6432 
        sslmode=verify-full 
        dbname=db-pc 
        user=user1 
        password=postgres 
        target_session_attrs=read-write 
    """)
    return conn

def get_primary_key(conn, table_name):
    query = """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY';
    """
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        primary_key = cur.fetchone()
        return primary_key[0] if primary_key else None



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table/<table_name>')
def table_view(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(f'SELECT * FROM {table_name};')
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    
    # Проверяем, является ли запрос AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('tables.html', table_name=table_name, data=data, column_names=column_names)
    
    return render_template('index.html', table_name=table_name, data=data, column_names=column_names)

@app.route('/delete/<table_name>/<int:row_id>', methods=['POST'])
def delete_row(table_name, row_id):
    conn = get_db_connection()
    primary_key = get_primary_key(conn, table_name)

    if not primary_key:
        return f"Ошибка: не удалось определить первичный ключ для таблицы {table_name}", 400

    cur = conn.cursor()
    query = f'DELETE FROM {table_name} WHERE {primary_key} = %s;'
    cur.execute(query, (row_id,))
    conn.commit()
    cur.close()
    conn.close()

    return table_view_ajax(table_name)


@app.route('/add/<table_name>', methods=['POST'])
def add_row(table_name):
    conn = get_db_connection()
    cur = conn.cursor()

    column_names = request.form.keys()
    values = [request.form[col] for col in column_names]

    columns_str = ', '.join(column_names)
    placeholders = ', '.join(['%s'] * len(values))
    query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders});'

    cur.execute(query, values)
    conn.commit()

    cur.close()
    conn.close()
    
    # Возвращаем обновлённую таблицу
    return table_view_ajax(table_name)

@app.route('/table_ajax/<table_name>')
def table_view_ajax(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(f'SELECT * FROM {table_name};')
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()
    
    return render_template('tables.html', table_name=table_name, data=data, column_names=column_names)

@app.route('/get_row/<table_name>/<int:row_id>', methods=['GET'])
def get_row(table_name, row_id):
    conn = get_db_connection()
    primary_key = get_primary_key(conn, table_name)

    if not primary_key:
        return f"Ошибка: не удалось определить первичный ключ для таблицы {table_name}", 400

    cur = conn.cursor()
    query = f'SELECT * FROM {table_name} WHERE {primary_key} = %s;'
    cur.execute(query, (row_id,))
    row = cur.fetchone()
    column_names = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    # Создаём словарь для передачи в шаблон
    row_dict = dict(zip(column_names, row))

    return render_template('edit_form.html', table_name=table_name, row=row_dict, primary_key=primary_key)

@app.route('/update/<table_name>/<int:row_id>', methods=['POST'])
def update_row(table_name, row_id):
    conn = get_db_connection()
    primary_key = get_primary_key(conn, table_name)

    if not primary_key:
        return f"Ошибка: не удалось определить первичный ключ для таблицы {table_name}", 400

    cur = conn.cursor()
    column_names = request.form.keys()
    values = [request.form[col] for col in column_names]

    set_clause = ', '.join([f'{col} = %s' for col in column_names])
    query = f'UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s;'

    cur.execute(query, values + [row_id])
    conn.commit()

    cur.close()
    conn.close()

    return table_view_ajax(table_name)

# выпадающие списки
@app.route('/get_options/<table_name>', methods=['GET'])
def get_options(table_name):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Получаем только два столбца: ID и описание
        query = f"SELECT * FROM {table_name};"
        cur.execute(query)
        data = cur.fetchall()

        # Предполагаем, что первый столбец — ID, второй — описание
        result = [{'id': row[0], 'name': row[1]} for row in data]
    except Exception as e:
        return {'error': str(e)}, 400
    finally:
        cur.close()
        conn.close()

    return {'data': result}



if __name__ == '__main__':
    app.run(debug=True)