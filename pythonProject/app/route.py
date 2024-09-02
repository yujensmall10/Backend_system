from flask import render_template, redirect, url_for, request, flash, current_app, session, jsonify,render_template_string, send_from_directory,g
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, Role, db, Article, Comment, Parts , Parts_Inventory ,Parts_Warehouse ,Inventory_Record, Clients
import os,base64,logging
from datetime import datetime ,timedelta
import requests
import asposecells
import json
import html


def custom_icons(filename):
    return send_from_directory('static/icons', filename)
def manifest():
    return send_from_directory('static', 'manifest.json')

def service_worker():
    return send_from_directory('static', 'service-worker.js')




@login_required
def index():
    permissions = {
        '主頁': {
            'icon': 'fa-home',
            'subpages': {
                'index_v1': '公告',
                'index_v2': '主頁示例二',
                'index_v3': '主頁示例三',
                'index_v4': '主頁示例四',
                '分機表1130627': '分機表'
            }
        },
        '工作報告': {
            'icon': 'fa-file-text',
            'subpages': {
                'layouts_Business_Office': '營業部',
                'layouts_Administration_Dept' :'管理部',
                'layouts_Engineering_Department':'廠務部',
                'layouts_Export_Department':'儲務部',
                'layouts_General_Accounting_Department':'財務部',
                'layouts_Productive_Department':'生管部',
                'layouts_Purchasing_Department':'採購部',
                'layouts_Quality_Department':'品管部',
                'searchreport': '日報'
            }
        },
        '業務管理': {
            'icon': 'fa-suitcase',
            'subpages': {
                'business_clients': '客戶管理',
    }
        },
        '工務零件': {
            'icon': 'fa-wrench',
            'subpages': {
                'engineering_Parts_Inventory': '零件倉庫信息',
                'parts_InOut': '庫存管理',
                'parts_Record': '進出庫紀錄',
                'part_Chart': '零件報表'
            }
        },
        '設置': {
            'icon': 'fa-cog',
            'subpages': {
                'role_management': '身分管理',
                'homepagemanage':'主頁管理'
            }
        },

    }
    user_permissions = session.get('user_permissions', [])
    print('Current session permissions:', user_permissions)  # 打印会话中的权限
    return render_template('index.html', permissions=permissions, user_permissions=user_permissions)

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)  # 启用记住我功能
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            session['user_role'] = user.role.name  # 将用户角色名称存储在会话中
            session['user_username'] = user.username
            session['user_permissions'] = user.role.permissions.split(',')
            print('User permissions:', session['user_permissions'])  # 打印会话中的权限
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type', 'user_permissions', 'user_role'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return render_template('login.html', clear_storage=True)

# ----------------------------------用戶端修改密碼----------------------------------
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        # 验证旧密码是否正确
        if not check_password_hash(current_user.password, old_password):
            return jsonify({'message': '舊密码不正確'}), 400

        # 验证新密码是否一致
        if new_password != confirm_new_password:
            return jsonify({'message': '新密码和確認密碼不一'}), 400

        # 更新密码
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({'message': '密码修改成功'})

    return render_template('change_password.html')

@login_required
def dashboard():
    return render_template('dashboard.html')

@login_required
def protected_route():
    return "This is a protected route."

@login_required
def role_management():
    roles = Role.query.all()
    users = User.query.all()
    permissions = {
        '主頁': {
            'index_v1': '公告',
            'index_v2': '主頁示例二',
            'index_v3': '主頁示例三',
            'index_v4': '主頁示例四',
            '分機表1130627': '分機表'
        },
        '工作報告': {
             'layouts_Business_Office': '營業部',
                'layouts_Administration_Dept' :'管理部',
                'layouts_Engineering_Department':'廠務部',
                'layouts_Export_Department':'儲務部',
                'layouts_General_Accounting_Department':'財務部',
                'layouts_Productive_Department':'生管部',
                'layouts_Purchasing_Department':'採購部',
                'layouts_Quality_Department':'品管部',
                'searchreport':'日報'
        },
        '業務管理': {
            'business_clients': '客戶管理',
            'view_all_clients': '查看所有客戶'
        },
        '工務零件': {
            'engineering_Parts_Inventory': '零件倉庫信息',
            'parts_InOut': '庫存管理',
            'parts_Record': '進出庫紀錄',
            'part_Chart':'零件報表'
        },
        '設置': {
            'role_management': '身分管理',
            'homepagemanage': '主頁管理'
        },

    }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role_id=role_id)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('role_management'))

    user_role = current_user.role.name if current_user.role else '未登录'
    user_permissions = session.get('user_permissions', [])
    return render_template('role_management.html', roles=roles, users=users, permissions=permissions, user_role=user_role)


# 主頁--------------------------------------------------------------------------------------------------------------------------------------------------------------------
@login_required
def 分機表1130627():
    return render_template('分機表1130627.html')
@login_required
def index_v2():
    return render_template('index_v2.html')

@login_required
def index_v1():
    return render_template('index_v1.html')

@login_required
def index_v3():
    return render_template('index_v3.html')

@login_required
def index_v4():
    return render_template('index_v4.html')

@login_required
def index_v5():
    return render_template('index_v5.html')

# 身分管理---------------------------------------------------------------------------------------------------------------------------------------------------------------
@login_required
def edit_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            user.username = request.form.get('username')
            password = request.form.get('password')
            if password:
                user.password = generate_password_hash(password)
            user.role_id = request.form.get('role_id')
            db.session.commit()
        else:
            flash('用户未找到', 'error')
    return redirect(url_for('role_management'))

@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role_id=role_id)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('role_management'))

@login_required
def add_role():
    if request.method == 'POST':
        role_name = request.form['role_name']
        selected_permissions = request.form.getlist('permissions')
        permissions_string = ','.join(selected_permissions)
        new_role = Role(name=role_name,  permissions=permissions_string)
        db.session.add(new_role)
        db.session.commit()
    return redirect(url_for('role_management'))

@login_required
def edit_role():
    if request.method == 'POST' and request.form.get('_method') == 'PUT':
        role_id = request.form.get('role_id')
        role = Role.query.get(role_id)
        if role:
            role.description = request.form.get('role_description') or role.description
            selected_permissions = request.form.getlist('permissions')
            role.permissions = ','.join(selected_permissions)
            db.session.commit()
    return redirect(url_for('role_management'))

@login_required
def get_role_permissions():
    role_id = request.args.get('role_id')
    role = Role.query.get(role_id)
    if role:
        permissions = role.permissions.split(',') if role.permissions else []
        return jsonify({'permissions': permissions})
    return jsonify({'permissions': []})
@login_required
def delete_role(role_id):
    role = Role.query.get(role_id)
    if role:
        db.session.delete(role)
        db.session.commit()
    return redirect(url_for('role_management'))
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('role_management'))

# 主頁管理-------------------------------------------------------------------------------------------------------------------------------------------------------------
def homepagemanage():
    return render_template('homepagemanage.html')


def upload():
    file = request.files['file']
    if file:
        # 保存上传的Excel文件
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)

        # 使用openpyxl读取Excel文件
        wb = load_workbook(filename=file_path)
        ws = wb.active

        # 获取列宽
        col_widths = {}
        for col in ws.columns:
            max_length = 0
            column = get_column_letter(col[0].column)  # 获取列的字母
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2  # 调整宽度
            col_widths[column] = adjusted_width

        # 处理合并单元格
        merged_cells = {str(range_.coord): range_ for range_ in ws.merged_cells.ranges}

        # 转换Excel内容为HTML
        html_content = '<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse;">'
        for row in ws.iter_rows():
            html_content += '<tr>'
            for cell in row:
                # 跳过合并的单元格
                if cell.coordinate in merged_cells and merged_cells[cell.coordinate].start_cell != cell.coordinate:
                    continue

                # 获取单元格颜色
                fill = cell.fill
                bg_color = None
                if fill and isinstance(fill, PatternFill) and fill.fgColor.type == 'rgb':
                    bg_color = fill.fgColor.rgb
                    if bg_color:
                        bg_color = f'#{bg_color[2:]}'

                cell_value = cell.value if cell.value is not None else ""
                cell_style = ""
                if bg_color:
                    cell_style += f'background-color: {bg_color};'
                col_letter = get_column_letter(cell.column)
                if col_letter in col_widths:
                    cell_style += f'width: {col_widths[col_letter]}px;'

                # 处理合并单元格的跨度
                if cell.coordinate in merged_cells:
                    cell_range = merged_cells[cell.coordinate]
                    rowspan = cell_range.max_row - cell_range.min_row + 1
                    colspan = cell_range.max_col - cell_range.min_col + 1
                    cell_html = f'<td style="{cell_style}" rowspan="{rowspan}" colspan="{colspan}">{html.escape(str(cell_value))}</td>'
                else:
                    cell_html = f'<td style="{cell_style}">{html.escape(str(cell_value))}</td>'

                html_content += cell_html
            html_content += '</tr>'
        html_content += '</table>'

        # 删除临时文件
        os.remove(file_path)

        return html_content
    return 'No file uploaded', 400

def send_static(path):
    return send_from_directory('static', path)

# 工作報告-------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required
def layouts_Engineering_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Engineering_Department.html',current_date=current_date)

@login_required
def layouts_Export_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Export_Department.html',current_date=current_date)

@login_required
def layouts_General_Accounting_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_General_Accounting_Department.html',current_date=current_date)

@login_required
def layouts_Productive_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Productive_Department.html',current_date=current_date)

@login_required
def layouts_Purchasing_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Purchasing_Department.html',current_date=current_date)

@login_required
def layouts_Quality_Department():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Quality_Department.html',current_date=current_date)

@login_required
def layouts_Business_Office():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Business_Office.html',current_date=current_date)

def layouts_Administration_Dept():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('layouts_Administration_Dept.html',current_date=current_date)
@login_required
def get_article_filename(date, department, title):
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    sanitized_title = title.replace(' ', '_')
    return os.path.join(current_app.root_path, 'articles', department, year_month, f"{date}-{sanitized_title}.html")



def searchreport():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('searchreport.html', current_date=current_date)
@login_required
def get_article():
    date = request.args.get('date')
    department = request.args.get('department')
    title = request.args.get('title').replace(' ', '_')  # 标题中的空格替换为下划线以匹配文件名

    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    articles_dir = os.path.join(current_app.root_path, 'articles', department, year_month)
    filename = os.path.join(articles_dir, f"{date}_{title}.html")

    # 調試日誌
    print(f"Looking for file: {filename}")

    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content, 'title': title.replace('_', ' ')})
        except Exception as e:
            print(f"Error reading article: {e}")
            return jsonify({'message': '读取失败'}), 500
    else:
        print(f"File not found: {filename}")
        return jsonify({'message': '文件不存在'}), 404

def get_article2():
    date = request.args.get('date')
    department = request.args.get('department')
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    articles_dir = os.path.join(current_app.root_path, 'articles', department, year_month)

    articles = []

    if os.path.exists(articles_dir):
        for filename in os.listdir(articles_dir):
            if filename.startswith(date):
                title = filename.split('_', 1)[1].replace('.html', '').replace('_', ' ')
                filepath = os.path.join(articles_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                articles.append({'title': title, 'content': content})

    return jsonify({'articles': articles})
@login_required
def save_article():
    data = request.get_json()
    date = data.get('date')
    department = data.get('department')
    title = data.get('title')
    content = data.get('content')

    if not date or not department or not title:
        return jsonify({'message': '日期、部门和标题不能为空'}), 400

    sanitized_title = title.replace(' ', '_')
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    articles_dir = os.path.join(current_app.root_path, 'articles', department, year_month)
    os.makedirs(articles_dir, exist_ok=True)
    filename = os.path.join(articles_dir, f"{date}_{sanitized_title}.html")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': '文章已保存'})
    except Exception as e:
        return jsonify({'message': '保存失败', 'error': str(e)}), 500

@login_required
def get_latest_articles():
    base_dir = os.path.join(current_app.root_path, 'articles')
    latest_articles = []
    cutoff_date = datetime.now() - timedelta(days=3)  # 获取三天前的日期

    for department in os.listdir(base_dir):
        department_dir = os.path.join(base_dir, department)
        if os.path.isdir(department_dir):
            latest_file = None
            latest_time = None

            for root, dirs, files in os.walk(department_dir):
                for file in files:
                    if file.endswith(".html"):
                        filename = os.path.basename(file)
                        try:
                            date_str, title = filename.split('_', 1)
                            file_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if file_date >= cutoff_date:  # 只显示三天内的文章
                                file_time = os.path.getmtime(os.path.join(root, file))
                                if latest_time is None or file_time > latest_time:
                                    latest_time = file_time
                                    latest_file = os.path.join(root, file)
                        except ValueError as e:
                            print(f"Skipping file with unexpected format: {filename}")
                            continue

            if latest_file:
                try:
                    title = title.replace('.html', '').replace('_', ' ')
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    latest_articles.append({
                        'department': department,
                        'date': date_str,
                        'title': title,
                        'content': content
                    })
                except ValueError as e:
                    print(f"Error processing file: {latest_file}")

    return jsonify({'articles': latest_articles})

@login_required
def get_reports():
    date = request.args.get('date')
    department = request.args.get('department')
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    articles_dir = os.path.join(current_app.root_path, 'articles', department, year_month)

    reports = []

    if os.path.exists(articles_dir):
        for filename in os.listdir(articles_dir):
            if filename.startswith(date):
                title = filename.split('_', 1)[1].replace('.html', '').replace('_', ' ')
                reports.append({'title': title})

    return jsonify({'reports': reports})

def view_reports():
    date = request.args.get('date')
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    base_articles_dir = os.path.join(current_app.root_path, 'articles')

    reports = []

    # 遍历所有部门目录
    for department in os.listdir(base_articles_dir):
        department_dir = os.path.join(base_articles_dir, department, year_month)
        if os.path.exists(department_dir):
            for filename in os.listdir(department_dir):
                if filename.startswith(date):
                    title = filename.split('_', 1)[1].replace('.html', '').replace('_', ' ')
                    reports.append({'department': department, 'title': title})

    return jsonify({'reports': reports})


@login_required
def view_report():
    filename = request.args.get('filename')
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    return jsonify({'content': '報告未找到'})

@login_required
def delete_article():
    data = request.get_json()
    date = data.get('date')
    department = data.get('department')
    title = data.get('title')

    if not date or not department or not title:
        return jsonify({'message': '日期、部门和标题不能为空'}), 400

    sanitized_title = title.replace(' ', '_')
    year_month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
    articles_dir = os.path.join(current_app.root_path, 'articles', department, year_month)
    filename = os.path.join(articles_dir, f"{date}_{sanitized_title}.html")

    # Debug log to check the generated file path
    print(f"Trying to delete file: {filename}")

    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"File deleted: {filename}")  # Debug log for successful deletion
            return jsonify({'message': '文章已删除'})
        except Exception as e:
            print(f"Error deleting file: {e}")  # Debug log for errors
            return jsonify({'message': '删除失败', 'error': str(e)}), 500
    else:
        print(f"File not found: {filename}")  # Debug log if file is not found
        return jsonify({'message': '文件不存在'}), 404
# 業務行程----------------------------------------------------------------------------------------------------------------------------------------------------------------
def business_Calendar():
    return render_template('business_Calendar.html')

# 工務零件庫存-------------------------------------------------------------------------------------------------------------------------------------------
@login_required
def engineering_Parts_Inventory():
    return render_template('engineering_Parts_Inventory.html')

@login_required
def get_parts():
    parts = Parts.query.all()
    parts_list = []
    for part in parts:
        parts_list.append({
            'id': part.id,
            'part_number': part.part_number,
            'name': part.name,
            'brand': part.brand,
            'usage': part.usage
        })
    return jsonify({'parts': parts_list})
def get_partid(id):
    part = Parts.query.get(id)
    if part:
        return jsonify({
            'id': part.id,
            'part_number': part.part_number,
            'name': part.name,
            'brand': part.brand,
            'usage': part.usage
        })
    return jsonify({'error': '零件未找到'}), 404

@login_required
def add_part():
    data = request.get_json()
    new_part = Parts(
        part_number=data['part_number'],
        name=data['name'],
        brand=data['brand'],
        usage=data['usage']
    )
    db.session.add(new_part)
    db.session.commit()
    return jsonify({'message': '零件添加成功'})

@login_required
def edit_part():
    data = request.json
    part = Parts.query.get(data['id'])
    if part:
        try:
            # 更新零件信息
            part.part_number = data['part_number']
            part.name = data['name']
            part.brand = data['brand']
            part.usage = data['usage']
            db.session.commit()

            # 同步更新出入库记录
            Inventory_Record.query.filter_by(part_id=part.id).update({
                'part_number': part.part_number,
                'name': part.name,
                'brand': part.brand,
                'usage': part.usage
            })
            db.session.commit()

            return jsonify({'success': '零件和相关记录已更新'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': '更新失败'}), 500
    return jsonify({'error': '零件未找到'}), 404
@login_required
def delete_part():
    data = request.json
    part_id = data['id']
    password = data['password']

    user = User.query.get(current_user.id)
    if not check_password_hash(user.password, password):
        return jsonify({'message': '密码錯誤'}), 400

    part = Parts.query.get(part_id)
    if part:
        db.session.delete(part)
        db.session.commit()
        return jsonify({'message': '零件删除成功'})
    return jsonify({'message': '零件未找到'}), 404

@login_required
def get_warehouses():
    warehouses = Parts_Warehouse.query.all()
    warehouses_data = [{'id': warehouse.id, 'name': warehouse.name, 'location': warehouse.location, 'principal': warehouse.principal} for warehouse in warehouses]
    return jsonify({'warehouses': warehouses_data})

@login_required
def add_warehouse():
    data = request.json
    new_warehouse = Parts_Warehouse(
        name=data['name'],
        location=data['location'],
        principal=data['principal']
    )
    db.session.add(new_warehouse)
    db.session.commit()
    return jsonify({'message': '倉庫信息添加成功'})

@login_required
def delete_warehouse():
    data = request.json
    warehouse_id = data['id']
    password = data['password']

    user = User.query.get(current_user.id)
    if not check_password_hash(user.password, password):
        return jsonify({'message': '密碼錯誤'}), 400

    warehouse = Parts_Inventory.query.get(warehouse_id)
    if warehouse:
        db.session.delete(warehouse)
        db.session.commit()
        return jsonify({'message': '倉庫删除成功'})
    return jsonify({'message': '倉庫未找到'}), 404

@login_required
def parts_InOut():
    return render_template('parts_InOut.html')

@login_required
def get_inventory():
    inventory = Parts_Inventory.query.all()
    inventory_data = []
    for item in inventory:
        inventory_data.append({
            'warehouse': item.warehouse,
            'part_number': item.part.part_number,
            'name': item.part.name,
            'brand': item.part.brand,
            'usage': item.part.usage,
            'quantity': item.quantity
        })
    return jsonify({'inventory': inventory_data})

@login_required
def get_parts_inventory():
    search = request.args.get('search', '')
    parts = Parts.query.filter(Parts.name.contains(search) | Parts.part_number.contains(search)).all()
    parts_data = [{'id': part.id, 'part_number': part.part_number, 'name': part.name} for part in parts]
    return jsonify({'parts': parts_data})

@login_required
def add_stock():

    data = request.json
    part_id = data['part_id']
    warehouse = data['warehouse']
    quantity = int(data['quantity'])
    in_date = datetime.strptime(data['inDateTime'], '%Y-%m-%dT%H:%M')
    member = session.get('user_username')
    gold = float(data['gold'])  # 确保gold字段被接收和处理

    existing_inventory = Parts_Inventory.query.filter_by(warehouse=warehouse, part_id=part_id, out_date=None).first()

    if existing_inventory:
        existing_inventory.quantity += quantity
        existing_inventory.in_date = in_date
        existing_inventory.member = member
    else:
        new_inventory_item = Parts_Inventory(
            warehouse=warehouse,
            part_id=part_id,
            quantity=quantity,
            in_date=in_date,
            member=member
        )
        db.session.add(new_inventory_item)

    part = Parts.query.get(part_id)
    new_record = Inventory_Record(
        warehouse=warehouse,
        operation_type='進庫',
        part_id=part_id,
        part_number=part.part_number,
        name=part.name,
        brand=part.brand,
        usage=part.usage,
        event_time=in_date,
        operation_time=datetime.utcnow() + timedelta(hours=8),
        quantity=quantity,
        member=member,
        gold=gold  # gold字段记录在记录表中
    )
    db.session.add(new_record)

    db.session.commit()
    return jsonify({'message': '進庫成功'})

@login_required
def remove_stock():
    data = request.json
    part_id = data['part_id']
    warehouse = data['warehouse']
    quantity = int(data['quantity'])
    out_date = datetime.strptime(data['outDateTime'], '%Y-%m-%dT%H:%M')
    out_member = data['out_member']
    reason = data['reason']
    gold = float(data['gold']) if 'gold' in data else 0.0

    inventory_item = Parts_Inventory.query.filter_by(warehouse=warehouse, part_id=part_id, out_date=None).first()

    if inventory_item and inventory_item.quantity >= quantity:
        inventory_item.quantity -= quantity
        if inventory_item.quantity == 0:
            inventory_item.out_date = out_date
            inventory_item.out_member = out_member
            inventory_item.reason = reason
        else:
            inventory_item.out_date = out_date
            inventory_item.out_member = out_member
            inventory_item.reason = reason

        part = Parts.query.get(part_id)
        new_record = Inventory_Record(
            warehouse=warehouse,
            operation_type='出庫',
            part_id=part_id,
            part_number=part.part_number,
            name=part.name,
            brand=part.brand,
            usage=part.usage,
            event_time=out_date,
            operation_time=datetime.utcnow() + timedelta(hours=8),
            quantity=quantity,
            member=out_member,
            reason=reason,
            gold=gold
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'message': '出庫成功'})
    return jsonify({'message': '數量不足或找不到對應的零件'}), 400

@login_required
def parts_Record():
    return render_template('parts_Record.html')

@login_required
def get_records():
    records = Inventory_Record.query.all()
    records_data = []
    for record in records:
        records_data.append({
            'warehouse': record.warehouse,
            'operation_type': record.operation_type,
            'part_number': record.part_number,
            'name': record.name,
            'brand': record.brand,
            'usage': record.usage,
            'event_time': record.event_time.strftime('%Y-%m-%d %H:%M'),
            'operation_time': record.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'quantity': record.quantity,
            'member': record.member,
            'reason': record.reason,
            'gold':record.gold
        })
    return jsonify({'records': records_data})

def part_Chart():
    return render_template('part_Chart.html')
@login_required
def get_monthly_costs():
    from sqlalchemy import func

    # 获取每月进库总金额（单价乘以数量）
    inbound_costs = db.session.query(
        func.strftime('%Y-%m', Inventory_Record.event_time).label('month'),
        func.sum(Inventory_Record.gold * Inventory_Record.quantity).label('total_inbound')
    ).filter(Inventory_Record.operation_type == '進庫').group_by('month').all()

    # 获取每月出库总金额（单价乘以数量）
    outbound_costs = db.session.query(
        func.strftime('%Y-%m', Inventory_Record.event_time).label('month'),
        func.sum(Inventory_Record.gold * Inventory_Record.quantity).label('total_outbound')
    ).filter(Inventory_Record.operation_type == '出庫').group_by('month').all()

    # 组织数据
    data = {
        'months': [],
        'inbound': [],
        'outbound': []
    }

    inbound_dict = {row.month: row.total_inbound for row in inbound_costs}
    outbound_dict = {row.month: row.total_outbound for row in outbound_costs}

    all_months = sorted(set(inbound_dict.keys()).union(set(outbound_dict.keys())))

    for month in all_months:
        data['months'].append(month)
        data['inbound'].append(inbound_dict.get(month, 0))
        data['outbound'].append(outbound_dict.get(month, 0))

    return jsonify(data)
# ------------------------------------------------------------------------------------------------------------------------------------------------------
def testphone():
    return render_template('testphone.html')

def save_changes():
    # 获取前端发送的数据并进行处理
    data = request.form.to_dict()
    # 进行数据保存操作（此处省略具体的保存逻辑）
    print(data)  # 打印数据以供调试
    return jsonify(success=True)

# 客戶---------------------------------------------------------------------------------------------------------------------------------------------------
def business_clients():
    print('Current user permissions:', session.get('user_permissions', []))
    if 'view_all_clients' in session.get('user_permissions', []):
        clients_list = Clients.query.all()
    else:
        clients_list = Clients.query.filter_by(whoadd=current_user.username).all()
    return render_template('business_clients.html', clients=clients_list)

def get_client_details(client_id):
    client = Clients.query.filter_by(id=client_id).first()
    if client:
        return jsonify({
            'clientname': client.clientname,
            'company': client.company,
            'contact': client.contact,
            'country': client.country,
            'introduction' : client.introduction
        })
    else:
        return jsonify({'error': 'Client not found'}), 404

def add_client():

    data = request.form  # 获取表单数据
    whoadd = current_user.username  # 假设这是当前登录用户，你需要根据实际情况替换
    clientname = data.get('clientname')
    company = data.get('company')
    contact = data.get('contact')
    country = data.get('country')
    introduction = data.get('introduction')

    if not clientname or not whoadd:
        return jsonify({"error": "Missing required fields"}), 400

    # 创建新的客户记录
    new_client = Clients(
        whoadd=whoadd,
        clientname=clientname,
        company=company,
        contact=contact,
        country=country,
        introduction=introduction
    )
    db.session.add(new_client)
    db.session.commit()  # 提交到数据库

    return jsonify({"message": "Client added successfully"}), 201

# 活動表單暫用--------------------------------------------------------------------------------------------------------------------------------------
def form1():
    return render_template('form1.html')

def thanks():
    return render_template('thanks.html')

def submit_form():
    try:
        data = {
            "entry.2021766921": request.form.get('name'),
            "entry.1984682984": request.form.get('score'),
            "entry.1893811687": request.form.get('choice'),
            "entry.2123727017": request.form.get('phone'),
            "entry.1215806286": request.form.get('familyname'),
            "entry.756881826": request.form.get('familyid'),
            "entry.960379202_year": request.form.get('familydob_year'),
            "entry.960379202_month": request.form.get('familydob_month'),
            "entry.960379202_day": request.form.get('familydob_day'),
            "entry.156057758": request.form.get('familyphone')
        }

        current_app.logger.debug(f"Form Data: {data}")  # 打印表单数据

        response = requests.post(
            "https://docs.google.com/forms/u/0/d/e/1FAIpQLSeT0z2rpcl1Rzwe80tnzq_TqKe93dZ3AGv2fbAPpHSUXftO0w/formResponse",
            data=data
        )

        if response.status_code == 200:
            return redirect("/thanks")
        else:
            return jsonify({"error": "Failed to submit form"}), response.status_code

    except Exception as e:
        current_app.logger.error(f"Error in submit_form: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# @login_required
# def get_articles():
#     date = request.args.get('date')
#     articles = Article.query.filter_by(date=date).all()
#     articles_list = [{'id': article.id, 'title': article.content.split('\n')[0]} for article in articles]
#     return jsonify(articles_list)
#
# @login_required
# def get_article_content():
#     article_id = request.args.get('article_id')
#     article = Article.query.get(article_id)
#     if article:
#         return jsonify({'content': article.content})
#     return jsonify({'content': ''}), 404
#
# @login_required
# def get_comments():
#     article_id = request.args.get('article_id')
#     comments = Comment.query.filter_by(article_id=article_id).all()
#     comments_list = [{'content': comment.content} for comment in comments]
#     return jsonify({'comments': comments_list})
#
# @login_required
# def add_comment():
#     data = request.get_json()
#     article_id = data.get('article_id')
#     content = data.get('content')
#
#     if not article_id or not content:
#         return jsonify({'success': False, 'message': '缺少文章ID或评论内容'}), 400
#
#     comment = Comment(article_id=article_id, content=content, created_at=datetime.utcnow())
#     db.session.add(comment)
#     db.session.commit()
#
#     return jsonify({'success': True, 'message': '评论已添加'})