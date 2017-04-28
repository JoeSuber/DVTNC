import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String


inventory_columns = {"MEID":"INTEGER PRIMARY KEY",
                     "OEM":"TEXT",
                     "SKU":"TEXT",
                     "IMEI":"TEXT",
                     "MODEL":"TEXT",
                     "HW_TYPE":"TEXT",
                     "IN_DATE":"TEXT",
                     "OUT_DATE":"TEXT",
                     "ARCHIVED":"TEXT",
                     "TesterName":"TEXT",
                     "DVTadmin":"TEXT",
                     "SERIAL_NUMBER":"TEXT",
                     "MSLSPC":"TEXT",
                     "Comment":"TEXT"
                     }



people_columns = {"BadgeID":"INTEGER PRIMARY KEY",
                  "Name":"TEXT",
                  "Department":"TEXT"}

db_tables = ["INVENTORY", "PEOPLE"]

db_columns = [inventory_columns, people_columns]
__dbfn__ = "DVTCinventory"
__sqlext__ = '.sqlite'
__sql_inventory_fn__ = os.getcwd() + os.sep + __dbfn__ + __sqlext__
__sqlfiles__ = [__sql_inventory_fn__]

engine = create_engine('sqlite:///'+__sql_inventory_fn__)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Person(Base):
    __tablename__ = "people"
    badge_id = Column(Integer(), primary_key=True)
    name = Column(String(55), index=True)
    department = Column(String(30))

class Phone(Base):
    __tablename__ = "devices"
    MEID = Column(String(28), primary_key=True)
    OEM = Column(String(50))
    SKU = Column(String(50))
    IMEI = Column(String(50))
    MODEL = Column(String(50))
    Hardware_Type = Column(String(50))
    In_Date = Column(String(50))
    Out_Date = Column(String(50))
    Archived = Column(String(50))
    TesterName = Column(String(50))
    DVT_Admin = Column(String(50))
    Serial_Number = Column(String(50))
    MSLPC = Column(String(50))
    Comment = Column(String(255))

device42 = Phone(MEID = '99000751003652',
               OEM = 'Motorolla',
               SKU = 'Moto',
               IMEI = '990007510036524',
               MODEL = 'SUX-9000',
               Hardware_Type = "Phone",
               In_Date = "September 11, 2001",
               Out_Date = "12/12/12",
               Archived = "",
               TesterName = "Joe Schmo",
               DVT_Admin = "Ivana Hugenkiss",
               Serial_Number = "1234567",
               MSLPC = "")

realperson = Person(badge_id = 1234,
                name = 'Joe Schmo',
                department = 'Gnomes of Zurich')

session.add(realperson)
session.add(device42)
session.commit()



