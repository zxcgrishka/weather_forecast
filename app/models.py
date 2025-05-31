from . import db

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=1)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<Search {self.city} ({self.count})>'