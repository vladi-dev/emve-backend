from app import db

class MavenSignup(db.Model):
    __tablename__ = 'maven_signups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ssn = db.Column(db.String(80))
    dob = db.Column(db.String(80))
    dl = db.Column(db.String(80))
    sex = db.Column(db.String(80))
    felony = db.Column(db.String(80))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'ssn': self.ssn,
            'dob': self.dob,
            'dl': self.dl,
            'sex': self.sex,
            'felony': self.felony
        }
