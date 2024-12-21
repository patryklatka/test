from flask_sqlalchemy import SQLAlchemy

# Inicjalizacja bazy danych
db = SQLAlchemy()

# Tabela z typami sensorów
class SensorsTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Nazwa sensora, np. 'Sterowanie światłem', 'Czujnik temperatury'


# Tabela z sensorami
class Sensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('sensors_types.id'), nullable=False)  # Typ sensora (klucz obcy do sensor_types)
    group = db.Column(db.Integer, nullable=False)  # Grupa sensora, np. 1, 2, 3

    # Relacje
    type = db.relationship('SensorsTypes', backref=db.backref('sensors', lazy=True))  # Powiązanie z tabelą sensor_types


# Tabela z aktualnym stanem sensorów (np. dla światła i wentylatora)
class SensorsStates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)  # Klucz obcy do sensorów
    state = db.Column(db.String(4), nullable=False)  # Stan sensora: 0 lub 1
    
    # Relacje
    sensor = db.relationship('Sensors', backref=db.backref('states', lazy=True))


# Tabela z pomiarami (np. dla temperatury i wilgotności)
class Measurements(db.Model):
    date = db.Column(db.DateTime, primary_key=True, nullable=False)  # Data i czas pomiaru
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)  # Klucz obcy do sensorów
    value = db.Column(db.Float, nullable=False)  # Wartość pomiaru

    # Relacje
    sensor = db.relationship('Sensors', backref=db.backref('measurements', lazy=True))

#######################################################################
typy_sensorow = ["Czujnik światła", "Wiatrak", "Czujnik temperatury", "Czujnik wilogtności"]

slownik_sensorow = {1: 1, 2: 1, 3: 1, 4: 1}

"""
Chwilowe uzupełnianie niezbednych tabel na start
"""
def populate_sensor_types(sensor_type_names):
    """
    Funkcja do uzupełnienia tabeli SensorsTypes na podstawie listy nazw typów.
    
    Args:
        sensor_type_names (list): Lista nazw typów sensorów do dodania.
    """
    for name in sensor_type_names:
        # existing_type = SensorsTypes.query.filter_by(name=name).first()
        # if not existing_type:
        new_type = SensorsTypes(name=name)
        db.session.add(new_type)
        print(f"Dodano nowy typ sensora: {name}")
        # else:
        #     print(f"Typ sensora '{name}' już istnieje.")
    db.session.commit()


def populate_sensors(sensor_group_to_type):
    """
    Funkcja do uzupełnienia tabeli Sensors na podstawie słownika grup i typów.
    
    Args:
        sensor_group_to_type (dict): Słownik, gdzie klucz to grupa sensora,
                                     a wartość to ID typu sensora (klucz obcy do SensorsTypes).
    """
    for type_id, group in sensor_group_to_type.items():
        # existing_sensor = Sensors.query.filter_by(group=group, type_id=type_id).first()
        # if not existing_sensor:
        new_sensor = Sensors(group=group, type_id=type_id)
        db.session.add(new_sensor)
        print(f"Dodano nowy sensor: grupa {group}, typ {type_id}")
        # else:
        #     print(f"Sensor z grupą {group} i typem {type_id} już istnieje.")
    db.session.commit()


#######################################################################


# Funkcja do aktualizacji stanu sensora
def update_sensor_state(sensor_id, state):
    """
    Funkcja do aktualizacji stanu sensora w bazie danych.
    """
    try:
        sensor_state = SensorsStates.query.filter_by(sensor_id=sensor_id).first()
        if sensor_state:
            # Jeśli stan już istnieje, zaktualizuj go
            sensor_state.state = state
        else:
            # Jeśli stan nie istnieje, utwórz nowy wpis
            sensor_state = SensorsStates(sensor_id=sensor_id, state=state)
            db.session.add(sensor_state)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating sensor state: {e}")


# Funkcja zwracająca wszystkie bieżace stany czujników on/off. 
def get_all_states():
    return SensorsStates.query.all()


def add_measurement(sensor_id, measurement_date, value):
    """
    Dodaje pomiar do tabeli Measurements i usuwa najstarsze dane, jeśli liczba przekracza 10.
    """
    try:
        # Dodaj nowy pomiar
        new_measurement = Measurements(sensor_id=sensor_id, date=measurement_date, value=value)
        db.session.add(new_measurement)
        db.session.commit()

        # Sprawdź liczbę pomiarów dla danego czujnika
        measurements = Measurements.query.filter_by(sensor_id=sensor_id).order_by(Measurements.date).all()
        if len(measurements) > 10:
            # Usuń najstarsze pomiary, jeśli liczba przekracza 10
            for measurement in measurements[:-10]:
                db.session.delete(measurement)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding measurement: {e}")
