
from flask import Flask, request, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql import func

app = Flask(__name__)

# Add database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///pubmed.db'
app.config['SECRET_KEY']= 'very secret key'

# Initialize the database
db=SQLAlchemy(app)
app.app_context().push()

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


# Create a models
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    years_xp = db.Column(db.Integer)
    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    records = db.relationship('Record', backref='recs')



@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/create_doctor', methods=['GET','POST'])
def create_doctor():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        specialization = request.form.get('specialization')
        years_xp = request.form.get('years_xp')
        
        new_doctor = Doctor(name=name,
                            email=email,
                            specialization=specialization,
                            years_xp=years_xp)
        db.session.add(new_doctor)
        db.session.commit()
        flash(f'{name} has been added successfully!', category='success')
        return redirect(url_for('doctor_list'))
    else:
        return render_template("/create_doctor.html")


@app.route('/doctor_list', methods=['GET','POST'])
def doctor_list():
    doctors_list = Doctor.query.all()
    return render_template('doctor_list.html', doctors_list=doctors_list)


@app.route('/delete_doctor/<int:id>', methods=['GET','POST'])
def delete_doctor(id):
    doctor_to_delete = Doctor.query.get_or_404(id)
    try:
        db.session.delete(doctor_to_delete)
        db.session.commit()
        flash(f'Doctor ({doctor_to_delete.name}) has been deleted successfully!', category='success')
        return redirect('/doctor_list')
    except:
        flash('Doctor has been deleted successfully!', category='error')
        return 'There was a problem deleting this task'


@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update_doctor(id):
    doctor_to_update = Doctor.query.get_or_404(id)
    if request.method == 'POST':
        doctor_to_update.name=request.form.get('name')
        doctor_to_update.email=request.form.get('email')
        doctor_to_update.specialization=request.form.get('specialization')
        doctor_to_update.years_xp=request.form.get('years_xp')
        db.session.commit()
        flash(f'{doctor_to_update.name} has been updated successfully!', category='success')
        return redirect('/doctor_list')
    else:
        return render_template('doctor_update.html', doctor=doctor_to_update)

@app.route('/create_record', methods=['GET','POST'])
def create_record():
    option_list=[]
    results = db.session.query(Doctor.name).all()
    for result in results:
        option_list.append(result[0])
        
    if request.method == 'POST':
        current_doctor_choice=request.form.get('doctor_id')
        doctor_id = db.session.query(Doctor).filter(Doctor.name == current_doctor_choice).first().id

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        data = request.form.get('data')
        new_record = Record(data=data,
                            first_name=first_name,
                            last_name=last_name,
                            doctor_id=doctor_id)
        db.session.add(new_record)
        db.session.commit()
        flash('Application has been added successfully!', category='success')
        return redirect(url_for('records_list'))
    else:
        return render_template("/create_appointment.html", option_list=option_list)
 
@app.route('/records_list', methods=['GET','POST'])
def records_list():
    records_list = Record.query.all()
    doctors_list= Doctor.query.all()
    #current_doctor_choice=request.form.get('doctor_id')
    #doctor_name = db.session.query(Doctor).filter(Doctor.name == current_doctor_choice).first().name
    return render_template('appointments_list.html', records_list=records_list, doctors_list=doctors_list)

@app.route('/record_update/<int:id>', methods = ['GET', 'POST'])
def record_update(id):
    option_list=[]
    results = db.session.query(Doctor.name).all()
    for result in results:
        option_list.append(result[0])
    record_to_update = Record.query.get_or_404(id)
    if request.method == 'POST':
        current_doctor_choice=request.form.get('doctor_id')
        try:
            doctor_id = db.session.query(Doctor).filter(Doctor.name == current_doctor_choice).first().id
            if doctor_id != None:
                record_to_update.doctor_id=doctor_id
        except:
            flash(f'You didn\'t select a doctor', category='error')
            return redirect(f'/record_update/{record_to_update.id}')
        record_to_update.first_name=request.form.get('first_name')
        record_to_update.last_name=request.form.get('last_name')
        record_to_update.data=request.form.get('data')
        record_to_update.date=func.now()
        db.session.commit()
        flash(f'Record \'{record_to_update.id}\' has been updated successfully!', category='success')
        return redirect('/records_list')
    else:
        return render_template('record_update.html', record=record_to_update, option_list=option_list)


@app.route('/delete_record/<int:id>', methods=['GET','POST'])
def delete_record(id):
    record_to_delete = Record.query.get_or_404(id)
    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        flash(f'Record \"{record_to_delete.id}\" has been deleted successfully!', category='success')
        return redirect('/records_list')
    except:
        return f'There was a problem deleting this record\"{record_to_delete.id}\"'



if __name__ == "__main__":
    app.run(debug=True)