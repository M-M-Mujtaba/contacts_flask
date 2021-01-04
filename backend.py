from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship , sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json

app = Flask(__name__)
Base = declarative_base()

engine = create_engine('sqlite:///contacts.db', echo = True)
Session = sessionmaker(bind=engine)

class Contacts(Base):
    __tablename__ = 'contacts'

    username = Column(String, primary_key= True, nullable = False)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)

    def __repr__(self):
        return json.dumps({"username":self.username, "first_name":self.first_name, "last_name":self.last_name})

class Email(Base):
    __tablename__ = 'email'

    def __init__(self, email):
        self.email = email

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    user = Column(String, ForeignKey('contacts.username'))

    contacts = relationship("Contacts", back_populates="email")

    def __repr__(self):
        return  self.email

Contacts.email = relationship("Email", order_by=Email.id, back_populates="contacts")
# dummy_contact = Contacts(username = "dummy1",first_name = "big",last_name =  "dummy")

# dummy_contact.email = [Email(email="dummy1@gmail.com"), Email(email="dumm1@hotmail.com")]
# session.add(dummy_contact)
# session.commit()


@app.route('/all_contacts')
def list_all_contacts():
    session = Session()
    contact_list ={'Contacts':[]}
    for contact in session.query(Contacts):
        contact_info = {"user_info":json.loads(repr(contact)), "email":[repr(email) for email in contact.email]}
        contact_list['Contacts'].append(contact_info)
        print(contact_info)
    return jsonify(contact_list)


@app.route('/contact', methods=['GET'])
def get_contact():
    session = Session()
    user = request.args.get('username')
    contact_info = None
    contact = session.query(Contacts).filter_by(username = user).first()
    contact_info = {"user_info":json.loads(repr(contact)), "email":[repr(email) for email in contact.email]}

    return jsonify(contact_info), 200

@app.route('/new_contact', methods=['POST'])
def creat_contact():
    session = Session()
    payload = json.loads(request.data)
    user_contact = Contacts(username = payload.get('username'), first_name = payload.get('first_name'), last_name= payload.get('last_name'))
    emails = payload.get('email', [])
    user_contact.email = [Email(email) for email in emails]
        
    session.add(user_contact)
    session.commit()
    contact_info = {"user_info":json.loads(repr(user_contact)), "email":[repr(email) for email in user_contact.email]}
    return jsonify(contact_info),  201


@app.route('/update_contact', methods=['PATCH'])
def modify_contact():
    session = Session()
    payload = json.loads(request.data)
    contact_info = None
    contact = session.query(Contacts).filter_by(username = payload["username"]).first()
    for attr in payload.keys():
        if attr != 'username':
            if attr == 'email':
                emails = payload.get('email', [])
                contact.email = [Email(email) for email in emails]    
            setattr(contact, attr, payload[attr])
    session.commit()
    return '', 204


@app.route('/delete_contact/<username>', methods=['DELETE'])
def remove_contact(username):
    session = Session()
    contact = session.query(Contacts).filter_by(username = username).first()
    for email in contact.email:
        session.delete(email)
    session.delete(contact)
    session.commit()
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)