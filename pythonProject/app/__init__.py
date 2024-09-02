from flask import Flask,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_principal import Principal
from datetime import timedelta
from .models import db, User, init_db, init_roles
from flask_migrate import Migrate
from flask_talisman import Talisman

def create_app():
    app = Flask(__name__,static_folder='static')
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=4)

    # 定义自定义过滤器
    def intersect_filter(list1, list2):
        return list(set(list1) & set(list2))

    # 注册自定义过滤器
    app.jinja_env.filters['intersect'] = intersect_filter

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    principals = Principal(app)

    from .route import (
        index, login, logout, dashboard, protected_route,custom_icons,homepagemanage,upload,send_static,change_password,delete_article,get_latest_articles,
        role_management, index_v2, edit_role, delete_user, add_role, add_user, edit_user,index_v1,index_v3,index_v4,index_v5,delete_role,view_reports
        ,layouts_Business_Office,layouts_Administration_Dept,get_article,save_article,get_role_permissions,layouts_Purchasing_Department,layouts_Quality_Department,layouts_Export_Department,layouts_Engineering_Department,layouts_Productive_Department,layouts_General_Accounting_Department
        ,view_report,get_reports,searchreport,get_article2,分機表1130627,business_Calendar,engineering_Parts_Inventory , get_parts,add_part,delete_part ,parts_InOut
        ,get_parts_inventory,add_stock, remove_stock, get_inventory ,get_warehouses,add_warehouse,delete_warehouse, parts_Record ,get_records, testphone ,business_clients, get_client_details ,manifest ,service_worker
        ,form1,submit_form,thanks,add_client,edit_part,get_partid,part_Chart,get_monthly_costs
    )


    app.add_url_rule('/manifest.json','manifest.json',manifest)
    app.add_url_rule('/service_worker.js', 'service_worker.js', service_worker)
    app.add_url_rule('/icons/<filename>', 'icons', custom_icons)
    # app.add_url_rule('/', 'index', index)
    app.add_url_rule('/index', 'index', index)
    # 登入
    app.add_url_rule('/', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/dashboard', 'dashboard', dashboard)
    # 修改密碼
    app.add_url_rule('/change_password', 'change_password', change_password, methods=['GET', 'POST'])
    # 網頁防護
    app.add_url_rule('/protected', 'protected_route', protected_route)
    # 身分認證
    app.add_url_rule('/role_management', 'role_management', role_management, methods=['GET', 'POST'])
    app.add_url_rule('/add_user', 'add_user', add_user, methods=['POST'])
    app.add_url_rule('/edit_user', 'edit_user', edit_user, methods=['POST'])
    app.add_url_rule('/delete_user/<int:user_id>', 'delete_user', delete_user)
    app.add_url_rule('/edit_role', 'edit_role', edit_role, methods=['POST'])
    app.add_url_rule('/add_role', 'add_role', add_role, methods=['POST'])
    app.add_url_rule('/delete_role/<int:role_id>', 'delete_role', delete_role)
    app.add_url_rule('/get_role_permissions', 'get_role_permissions', get_role_permissions)
    # 主頁管理
    app.add_url_rule('/homepagemanage', 'homepagemanage', homepagemanage)
    app.add_url_rule('/upload', 'upload', upload,methods=['POST'])
    app.add_url_rule('/send_static', 'send_static', send_static)

    # 主頁
    app.add_url_rule('/index_v1', 'index_v1', index_v1)
    app.add_url_rule('/index_v2', 'index_v2', index_v2)
    app.add_url_rule('/index_v3', 'index_v3', index_v3)
    app.add_url_rule('/index_v4', 'index_v4', index_v4)
    app.add_url_rule('/index_v5', 'index_v5', index_v5)
    app.add_url_rule('/分機表1130627', '分機表1130627', 分機表1130627)
    # 工作報告
    app.add_url_rule('/layouts_Business_Office', 'layouts_Business_Office', layouts_Business_Office)
    app.add_url_rule('/get_article', 'get_article', get_article, methods=['GET'])
    app.add_url_rule('/save_article', 'save_article', save_article, methods=['POST'])
    app.add_url_rule('/delete_article', 'delete_article', delete_article, methods=['DELETE'])
    app.add_url_rule('/get_latest_articles', 'get_latest_articles', get_latest_articles)
    app.add_url_rule('/layouts_Administration_Dept', 'layouts_Administration_Dept', layouts_Administration_Dept )
    app.add_url_rule('/layouts_Engineering_Department', 'layouts_Engineering_Department', layouts_Engineering_Department)
    app.add_url_rule('/layouts_Export_Department', 'layouts_Export_Department', layouts_Export_Department)
    app.add_url_rule('/layouts_General_Accounting_Department', 'layouts_General_Accounting_Department', layouts_General_Accounting_Department)
    app.add_url_rule('/layouts_Productive_Department', 'layouts_Productive_Department', layouts_Productive_Department)
    app.add_url_rule('/layouts_Purchasing_Department', 'layouts_Purchasing_Department', layouts_Purchasing_Department)
    app.add_url_rule('/layouts_Quality_Department', 'layouts_Quality_Department', layouts_Quality_Department)
    app.add_url_rule('/view_reports', 'view_reports', view_reports, methods=['GET'])
    # app.add_url_rule('/add_comment', 'add_comment', add_comment)
    # app.add_url_rule('/get_article_content', 'get_article_content', get_article_content)
    # app.add_url_rule('/get_comments', 'get_comments', get_comments)
    # app.add_url_rule('/layouts_Quality_Department', 'layouts_Quality_Department', layouts_Quality_Department)
    # app.add_url_rule('/get_articles', 'get_articles', get_articles)
    app.add_url_rule('/searchreport', 'searchreport', searchreport,methods=['GET'])
    app.add_url_rule('/get_reports', 'get_reports', get_reports,methods=['GET'])
    app.add_url_rule('/get_article2', 'get_article2', get_article2, methods=['GET'])
    # 業務行程
    app.add_url_rule('/business_Calendar', 'business_Calendar', business_Calendar)
    app.add_url_rule('/add_client', 'add_client', add_client, methods=['POST'])
    # 工務庫存
    app.add_url_rule('/engineering_Parts_Inventory', 'engineering_Parts_Inventory', engineering_Parts_Inventory)
    app.add_url_rule('/get_parts', 'get_parts', get_parts, methods=['GET'])
    app.add_url_rule('/get_partid/<int:id>', 'get_partid', get_partid, methods=['GET'])
    app.add_url_rule('/add_part', 'add_part', add_part, methods=['POST'])
    app.add_url_rule('/edit_part', 'edit_part', edit_part, methods=['POST'])
    app.add_url_rule('/delete_part', 'delete_part', delete_part, methods=['POST'])
    app.add_url_rule('/get_warehouses', 'get_warehouses', get_warehouses, methods=['GET'])
    app.add_url_rule('/add_warehouse', 'add_warehouse', add_warehouse, methods=['POST'])
    app.add_url_rule('/delete_warehouse', 'delete_warehouse', delete_warehouse, methods=['POST'])
    # 工務庫存-進出庫
    app.add_url_rule('/parts_InOut', 'parts_InOut', parts_InOut)
    app.add_url_rule('/get_inventory', 'get_inventory', get_inventory, methods=['GET'])
    app.add_url_rule('/get_parts_inventory', 'get_parts_inventory', get_parts_inventory, methods=['GET'])
    app.add_url_rule('/add_stock', 'add_stock', add_stock, methods=['POST'])
    app.add_url_rule('/remove_stock', 'remove_stock', remove_stock, methods=['POST'])
    # 工務庫存-進出庫紀錄
    app.add_url_rule('/parts_Record', 'parts_Record', parts_Record)
    app.add_url_rule('/get_records', 'get_records', get_records, methods=['GET'])
    app.add_url_rule('/testphone', 'testphone', testphone)
    app.add_url_rule('/business_clients', 'business_clients', business_clients)
    app.add_url_rule('/get_client_details/<int:client_id>', 'get_client_details', get_client_details, methods=['GET'])
    # 庫存報表
    app.add_url_rule('/part_Chart', 'part_Chart', part_Chart)
    app.add_url_rule('/get_monthly_costs', 'get_monthly_costs', get_monthly_costs, methods=['GET'])
    # 表單
    app.add_url_rule('/form1', 'form1', form1)
    app.add_url_rule('/thanks', 'thanks', thanks)
    app.add_url_rule('/submit_form', 'submit_form', submit_form, methods=['POST'])

    # 添加Talisman以强制使用HTTPS
    Talisman(app, content_security_policy=None)

    @app.after_request
    def add_csp(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.datatables.net cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.linearicons.com;"
            "connect-src 'self'; "
            "frame-src 'self' https://bs.cjf.com.tw:8000; "  # 允许来自 https://bs.cjf.com.tw:8000 的内容在 iframe 中嵌入
            "object-src 'none'; "
            "media-src 'self'; "
            "child-src 'self'; "
            "form-action 'self'; "
            "base-uri 'self';"
            "worker-src 'self'; "
        )
        return response
    # 添加重定向到HTTPS的before_request钩子
    @app.before_request
    def before_request():
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    with app.app_context():
        init_db()
        init_roles()

    return app
