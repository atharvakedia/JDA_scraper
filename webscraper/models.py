# models.py
from webscraper import db
from datetime import datetime

class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    schemes_cnt = db.Column(db.Integer)
    # Relationship: Each Zone has many Scheme objects.
    # The backref 'zone' allows each Scheme instance to access its related Zone as scheme.zone.
    schemes = db.relationship('Scheme', backref='zone', lazy=True)

    def __repr__(self):
        return f"Zone('{self.id}', '{self.name}', '{self.schemes_cnt}')"


class Scheme(db.Model):
    # Composite primary key: sch_id and sector_id.
    sch_id = db.Column(db.Integer, primary_key=True)
    sector_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # Renamed from 'zone' to 'zone_name' to store the zone name (string) and avoid conflict with the relationship.
    zone_name = db.Column(db.String(50))
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'))
    developer = db.Column(db.String(100))
    dev_type = db.Column(db.String(100))
    status = db.Column(db.String(50))
    plots = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"Scheme('{self.sch_id}', '{self.sector_id}', '{self.zone_name}', "
                f"'{self.developer}', '{self.status}', '{self.plots}')")


class Allotment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('scheme.sch_id'))
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'))
    plot_no = db.Column(db.String(100))
    owner = db.Column(db.String(500))
    use_desc = db.Column(db.String(50))
    possession_date = db.Column(db.Date)
    possession_area = db.Column(db.String(50))
    patta_date = db.Column(db.Date)
    patta_area = db.Column(db.String(50))
    allotment_date = db.Column(db.Date)
    allotment_area = db.Column(db.String(50))
    freehold_date = db.Column(db.Date)
    freehold_area = db.Column(db.String(50))

    def __repr__(self):
        return (f"Allotment('{self.id}', '{self.scheme_id}', '{self.zone_id}', "
                f"'{self.plot_no}', '{self.owner}', '{self.use_desc}', "
                f"'{self.possession_date}/{self.possession_area}', "
                f"'{self.patta_date}/{self.patta_area}', "
                f"'{self.allotment_date}/{self.allotment_area}', "
                f"'{self.freehold_date}/{self.freehold_area}')")