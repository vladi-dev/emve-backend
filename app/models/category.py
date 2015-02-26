from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))
    establishments = db.relationship('Establishment', backref='category')

    def __unicode__(self):
        return self.name
