# DVTNC

Implement Database Tables or Mongo

make crude interface screen
  user login with barcode
    (unknown user add)
  menu: display user 1)checkin device 2)checkout device
    show fields current state
    allow edit of fields
    
login, checkin, and checkout logic

export-to-excel function
  Sort by manufacturer (different fields available)

import from excel function
  parse the MEID field into int if CR or () in cell
  ensure MEID are unique.
  allow update/add from spreadsheet
  
make web server for interface

research the color codes in cells

# Database 

● OEM ○ Name of manufacturer

● MODEL ○ Model of device 

● MEID ○ Mobile Equipment Identifier 

● HW_TYPE ○ Hardware Type - Smartphone, Feature phone, Tablet, Module, etc. 

● SKU ○ Network that the device was designed for (Sprint, Boost, etc.) 

● STATUS ○ IN -- checked into inventory ○ OUT -- checked out of inventory for testing ○ ARCHIVED - the device is no longer at DVT&C

● OWNER ○ TesterName - name of the person who has the device ○ DVT Admin - the default owner when the device is still in inventory 

● SERIAL NUMBER

● MSL/SPC

● Device hand off - one employee takes a device from another and transfers it to their user ID in the inventory system. 

● System notification to entire team, via email, of current status of inventory every Friday at noon. 

● System notifies employee and administrator, via email, of the devices checked out under that employee’s badge ID after 14 days. 

● Secure logins differentiating permissions between the system administrator and an employee (tester, project
manager, staff engineer). 
