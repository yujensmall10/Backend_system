from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from datetime import datetime

db = SQLAlchemy()

# 角色管理表------------------------------------------------------------------------------------------------
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    permissions = db.Column(db.String(500), nullable=True)  # 逗号分隔的权限字符串

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

# 文章管理表---------------------------------------------------------------------------------------------------------------------------------------------------------------
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.date}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    article = db.relationship('Article', backref=db.backref('comments', lazy=True))

# 庫存管理表--------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Parts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    usage = db.Column(db.String(200), nullable=True)

class Parts_Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse = db.Column(db.String(80), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    part = db.relationship('Parts', backref=db.backref('inventory_items', lazy=True))
    in_date = db.Column(db.Date, nullable=False)
    member = db.Column(db.String(100), nullable=False)
    out_date = db.Column(db.Date, nullable=True)
    out_member = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)

class Parts_Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    principal = db.Column(db.String(200), nullable=True)

class Inventory_Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse = db.Column(db.String(80), nullable=False)
    operation_type = db.Column(db.String(10), nullable=False)  # "in" 或 "out"
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    part = db.relationship('Parts', backref=db.backref('inventory_records', lazy=True))
    part_number = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    usage = db.Column(db.String(200), nullable=True)
    event_time = db.Column(db.DateTime, nullable=False)  # 入庫或出庫時間
    operation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 操作時間
    quantity = db.Column(db.Integer, nullable=False)
    member = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(200), nullable=True)  # 出庫原因，入庫可為空
    gold = db.Column(db.Float)

# 客戶表------------------------------------------------------
class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    whoadd = db.Column(db.String(80), nullable=False)
    clientname = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=True)
    contact = db.Column(db.String(80), nullable=True)
    country = db.Column(db.String(80), nullable=True)
    introduction = db.Column(db.String(80), nullable=False)


# 初始化數據庫
def init_db():
    # Parts.__table__.drop(db.engine)   # 零件表初始化
    # Inventory_Record.__table__.drop(db.engine) # 進入庫紀錄表初始化
    # Parts_Inventory.__table__.drop(db.engine)  # 零件庫存表初始化
    Clients.__table__.drop(db.engine)
    db.create_all()

# 初始化角色數據和超級管理員
def init_roles():
    if Role.query.count() == 0:
        roles = [
            Role(name='業務部組長', description='管理業務部'),
            Role(name='儲備部組長', description='管理儲備部'),
            Role(name='管理部組長', description='管理管理部'),
            Role(name='總經理', description='公司總經理')
        ]
        db.session.add_all(roles)
        db.session.commit()

    if User.query.filter_by(username='admin').first() is None:
        super_admin_role = Role.query.filter_by(name='總經理').first()
        admin = User(username='admin', password=generate_password_hash('admin'), role=super_admin_role)
        db.session.add(admin)
        db.session.commit()
