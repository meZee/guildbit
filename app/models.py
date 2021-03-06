import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, index=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    duration = db.Column(db.Integer)
    password = db.Column(db.String)
    status = db.Column(db.String, default='active')
    type = db.Column(db.String, default='temp')
    mumble_host = db.Column(db.String, default="mumble.guildbit.com")
    mumble_instance = db.Column(db.Integer)
    cvp_uuid = db.Column(db.String, unique=True, index=True, default=None)
    ip = db.Column(db.String(64))
    extensions = db.Column(db.SmallInteger, default=0)

    ratings = db.relationship('Rating', backref='server', lazy='dynamic')

    @hybrid_property
    def expiration(self):
        return self.created_date + datetime.timedelta(hours=self.duration)

    @hybrid_property
    def is_expired(self):
        now = datetime.datetime.utcnow()
        exp = self.created_date + datetime.timedelta(hours=self.duration)
        return now > exp

    def __repr__(self):
        return '<Server %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(40), unique=True)
    nickname = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_role(self):
        return self.role

    def get_role_name(self):
        if self.role == 0:
            role_name = "user"
        elif self.role == 1:
            role_name = "admin"
        else:
            role_name = "unassigned"
        return role_name

    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db.session.add(rv)
        return rv

    def __repr__(self):
        return '<User %r>' % self.nickname


class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    message_type = db.Column(db.String(120), index=True)
    message = db.Column(db.String)
    location = db.Column(db.String(120), index=True, unique=True)

    def __init__(self, message_type, message, location):
        self.message_type = message_type
        self.message = message
        self.location = location

    def __repr__(self):
        return '<Notice %r>' % self.id


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_uuid = db.Column(db.String, db.ForeignKey('server.uuid'), index=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ip = db.Column(db.String(64))
    stars = db.Column(db.Integer)
    feedback = db.Column(db.String())

    def __repr__(self):
        return '<Rating %r>' % self.id


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, index=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    activation_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(120))
    package = db.Column(db.String(32))

    def __repr__(self):
        return '<Token %r>' % self.id



# class Host(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     hostname = db.Column(db.String(120), unique=True, index=True)
#     status = db.Column(db.String, default='active')
#     contact_name = db.Column(db.String(120))
#     contact_email = db.Column(db.String(120))
#     created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#
#     def __repr__(self):
#         return '<Host %r>' % self.hostname

