# webscraper/routes.py
from flask import render_template, request, redirect, url_for, flash
from webscraper import app, db
from webscraper.models import Zone, Scheme
import requests
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update')
def update():
    messages = []

    zone_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 20, 27, 28]
    
    for i in zone_ids:
        zone_url = f'https://api.jaipurjda.org/APICPRMS/api/CPRMSAPI/GetCPRMSSchemeDetails?SchemeName=&DeveloperTypeId=&DeveloperId=&ZoneId={i}'
        try:
            response = requests.get(zone_url)
            response.raise_for_status()
        except requests.RequestException as e:
            messages.append(f"Failed to retrieve data for zone ID {i}: {e}")
            continue
        
        data = response.json()
        all_schemes = data.get('Data', [])
        if not all_schemes:
            messages.append(f"No schemes found for zone ID {i}")
            continue
        
        new_count = len(all_schemes)
        zone_name = all_schemes[0]['ZName']
        
        # Retrieve or create the Zone record
        zone = Zone.query.get(i)
        if zone:
            if not zone.name:
                zone.name = zone_name
        else:
            zone = Zone(id=i, name=zone_name, schemes_cnt=new_count)
            db.session.add(zone)
        
        # Determine existing schemes for this zone
        existing_schemes = Scheme.query.filter_by(zone_id=i).all()
        existing_keys = {(s.sch_id, s.sector_id) for s in existing_schemes}
        new_keys = {(int(scheme['SchId']), int(scheme['SectorId'])) for scheme in all_schemes}
        
        to_add = new_keys - existing_keys
        to_update = new_keys & existing_keys
        
        # Insert new schemes
        for scheme in all_schemes:
            key = (int(scheme['SchId']), int(scheme['SectorId']))
            if key in to_add:
                new_scheme = Scheme(
                    sch_id=int(scheme['SchId']),
                    sector_id=int(scheme['SectorId']),
                    name=scheme['SchName'],
                    zone=scheme['ZName'],
                    zone_id=int(scheme['ZoneId']),
                    developer=scheme['DeveloperName'],
                    dev_type=scheme['DevTypeDesc'],
                    status=scheme['SchemeStatus'],
                    plots=int(scheme['TotalPlot']),
                    last_updated=datetime.utcnow()
                )
                db.session.add(new_scheme)
        
        # Update existing schemes if status has changed
        for scheme in all_schemes:
            key = (int(scheme['SchId']), int(scheme['SectorId']))
            if key in to_update:
                existing_scheme = Scheme.query.filter_by(sch_id=key[0], sector_id=key[1]).first()
                if existing_scheme and existing_scheme.status != scheme['SchemeStatus']:
                    existing_scheme.status = scheme['SchemeStatus']
                    existing_scheme.last_updated = datetime.utcnow()
                    messages.append(f"Updated scheme {key} in zone {zone_name}")
        
        zone.schemes_cnt = new_count
        db.session.commit()
        messages.append(f"Zone {zone_name} updated: {len(to_add)} new schemes added.")
    
    return render_template('update.html', messages=messages)

@app.route('/zones')
def zones():
    zones = Zone.query.all()
    return render_template('zones.html', zones=zones)

@app.route('/zone/<int:zone_id>')
def zone(zone_id):
    schemes = Scheme.query.filter_by(zone_id=zone_id).all()
    return render_template('zone.html', zone_id=zone_id, schemes=schemes)

@app.route('/timely', methods=['GET', 'POST'])
def timely():
    if request.method == 'POST':
        time_str = request.form.get('time')
        try:
            time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash("Incorrect time format. Please use YYYY-MM-DD HH:MM:SS")
            return redirect(url_for('timely'))
        schemes = Scheme.query.filter(Scheme.last_updated > time_obj).all()
        return render_template('timely.html', schemes=schemes, time_str=time_str)
    return render_template('timely.html')

@app.route('/custom_query', methods=['GET', 'POST'])
def custom_query():
    results = None
    query = ""
    error = None
    if request.method == 'POST':
        query = request.form.get('query')
        try:
            # Use SQLAlchemy's text() function for raw queries
            from sqlalchemy import text
            result_proxy = db.session.execute(text(query))
            results = result_proxy.fetchall()
        except Exception as e:
            error = str(e)
    return render_template('custom_query.html', results=results, query=query, error=error)