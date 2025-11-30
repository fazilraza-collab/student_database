🎓 Coaching Management System (DBMS + Streamlit + MySQL)

A complete Coaching Institute ERP System designed using MySQL, Python, and Streamlit to manage students, attendance, fees, batches, faculty, tests, results, and more.


---

📌 Project Overview

This project is a full-featured Coaching Management System built to digitalize and automate the daily operations of a coaching institute.
It focuses on giving admin, faculty, and management a single unified platform to manage all academic and administrative tasks efficiently.


---

🚀 Features (Modules Included)

1️⃣ Student Management

Add, update, delete students

Assign course & batch

Parent information

Active/Inactive status

Course-wise student summary



---

2️⃣ Attendance Management

Mark daily attendance

Date-range filter

Student-wise attendance

Attendance trend graph (Present % over time)



---

3️⃣ Fee Management

Record fee payments (UPI/Cash/Online)

Auto calculate pending fees

Monthly fee collection chart

Course-wise revenue insights



---

4️⃣ Course & Batch Management

Maintain detailed course structure

Fees, duration, categories

Batch creation & student assignment



---

5️⃣ Faculty & Class Scheduling

Assign faculty to subjects and classes

Room allocation

Class timetable generation

Faculty workload dashboard

Room utilization report



---

6️⃣ Test & Result Management

Add tests for each course

Enter marks and grades

Test-wise and student-wise performance tracking



---

7️⃣ Lead Management (CRM)

Track inquiries

Follow-up activities

Demo classes

Lead status & source analysis

Lead conversion insights



---

8️⃣ Room & Resource Allocation

Maintain coaching rooms (101, 102, Lab-1, etc.)

Allocate rooms for classes

Prevent timetable conflicts



---

9️⃣ Universal Table Viewer (In-App)

An inbuilt interface to view all MySQL tables inside Streamlit:

Search inside any table

Apply filters

Download CSV

CRUD support for selected modules



---

🛠 Tech Stack

Component	Technology

Backend	Python
Frontend	Streamlit
Database	MySQL
ORM/Driver	mysql-connector-python
Data Processing	Pandas



---

🗂 Database Schema (Major Tables)

student

attendance

course

batch

faculty

class_schedule

fee_payment

result

lead

lead_source

lead_activity

room


Fully normalized with foreign keys and relational mapping.


---

📊 Dashboards Included

Student summary

Attendance chart

Fee analytics

Course distribution

Lead conversion statistics

Faculty workload

Room booking visualization



---

📥 Installation & Setup

1. Clone the repository

git clone https://github.com/your-username/coaching-management-system.git
cd coaching-management-system

2. Install required packages

pip install -r requirements.txt

3. Update database credentials

In db.py or inside app:

DB_HOST = "your-host"
DB_USER = "your-user"
DB_PASSWORD = "your-password"
DB_NAME = "your-db"

4. Run the Streamlit App

streamlit run app.py


---

📌 Why This Project Is Useful

Completely removes manual registers & Excel dependency

Saves time for faculty & admin staff

Ensures accurate attendance, fees, and scheduling

Helps management make data-driven decisions

Suitable for real coaching centers

Easy to extend into full ERP



---

🎯 Who Can Use This Project

Coaching Institutes

Schools/Training Centers

Tuition Centers

Admin & Management teams

Students learning DBMS + Python



---

🔮 Future Enhancements

Automated SMS/Email notifications

Attendance QR code system

Faculty payroll management

Student Portal (login-based)

Online test system fully integrated



---

🤝 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss your idea.


---

📄 License

This project is open-source and available under the MIT License.
