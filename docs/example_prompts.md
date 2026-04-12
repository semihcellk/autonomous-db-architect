# 🎭 Example Prompts for DB-Architect

The **Autonomous DB-Architect** thrives on natural language. You can describe your application's domain in plain English, and the multi-agent system will extract the exact database tables, fields, and relationships needed to build a robust architecture. 

Here are some comprehensive example prompts you can test the system with:

### 1. 🛒 E-Commerce & Marketplace
> "I need a database for an e-commerce platform like Amazon. There should be users who can have multiple shipping addresses. Users can place orders. Each order contains multiple order items, and each item references a product. Products belong to categories. We also need to track payments linked to orders, including payment status and payment method, as well as product reviews left by users."

### 2. 🏥 Hospital Management System
> "Design a database for a hospital. We have doctors and patients. A doctor has a specialty and a room number. Patients have medical history records. Doctors can schedule appointments with patients. When an appointment occurs, a doctor might write a prescription that contains multiple medications. We also need a billing table to track invoices for each patient's visits."

### 3. 🐦 Social Media Platform
> "I want to build a social network. Users have profiles with a bio and avatar. Users can write posts with content and timestamps. Users can follow each other. Posts can have multiple likes and comments from other users. Also, include a notification system where users get notified when someone likes their post or follows them."

### 4. 🎓 University Course Registration
> "Create a course registration system for a university. We have students, professors, and departments. A professor belongs to a department. Professors teach courses. Each course can have multiple prerequisites (other courses). Students enroll in courses and receive grades. The system should also keep track of classrooms where the courses are held, including capacity and building name."

### 5. 💼 HR and Payroll Administration
> "Design an HR system. The company has multiple departments and branch locations. Employees work in a department and report to a manager (who is also an employee). We need to track employee attendance, leave requests (vacation, sick days) including approval status, and monthly payroll/salary slips with deductions and bonuses."

### 6. 🏨 Hotel Reservation System
> "I'm building a hotel booking system. The hotel has various room types (e.g., standard, deluxe, suite), and actual rooms are tied to these types. Guests can make bookings for a specific room over a date range. We need to track the payment for the booking, as well as additional charges for room service or amenities ordered during their stay."

### 7. 📚 Library Management
> "We need a database to manage a city library. The library has books, which can have multiple physical copies. Each book has authors, a publisher, and belongs to genres. Library members can borrow a specific physical copy of a book. The loan record should have a checkout date and a due date. If it's returned late, a fine is generated and linked to the loan."

### 8. 🚀 SaaS Subscription & Billing
> "Design a database for a B2B SaaS platform. Businesses (Tenants) register on the platform. Each tenant has multiple user accounts with roles. The tenant is subscribed to a specific Pricing Plan. We also need an invoices table for monthly recurring billing, and a feature usage log table to measure API calls made by each tenant."

---
*Tip: Copy any of these blocks and paste them into the terminal when `main.py` asks for a database definition!*
