from PiControl import db

class Config(db.Model):
    __tablename__   = 'config'
    id              = db.Column(db.Integer, primary_key=True)
    beacon_interval = db.Column(db.Integer, unique=True, nullable=False, default=60)
    beacon_port     = db.Column(db.Integer, unique=True, nullable=False, default=31415)
    secret_key      = db.Column(db.String(128), unique=True, nullable=False, default='PiControl')
    log_file        = db.Column(db.String(128), unique=True, nullable=False, default='logs/PiControl.log')
    log_level       = db.Column(db.Integer, unique=True, nullable=False, default=1)

    def __repr__(self):
        return '<Config %r>' % self.id
