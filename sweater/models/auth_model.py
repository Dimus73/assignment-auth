from sweater import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)  # Changed from username to email
    password = db.Column(db.String(256), nullable=False)
    token = db.relationship('Token', backref='user', lazy=True)
    owner_company = db.relationship('Company', backref='owner', lazy=True)
    memberships = db.relationship('CompanyMembers', backref='member', lazy=True)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refresh_token = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

