from PiControl import db

class Node(db.Model):
    __tablename__ = 'nodes'
    id           = db.Column(db.Integer, primary_key=True)
    ipaddress    = db.Column(db.String(12), unique=True, nullable=False)
    hostname     = db.Column(db.String(120), unique=False, nullable=False)
    revision     = db.Column(db.String(16), unique=False, nullable=False)
    last_checkin = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return '<Node %r>' % self.id
