import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "student_db")
    )

def fetch_payment_details(student_id: int) -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT student_name, amount_due, payment_status, last_payment_date FROM payments WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        record = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if record:
            return f"Student: {record['student_name']}, Amount Due: {record['amount_due']}, Status: {record['payment_status']}, Last Payment Date: {record['last_payment_date']}"
        else:
            return f"No payment record found for Student ID: {student_id}."
    except Exception as e:
        return f"Database error: {str(e)}"

def log_complaint(student_id: int, issue: str) -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO complaints (student_id, issue_description) VALUES (%s, %s)"
        cursor.execute(query, (student_id, issue))
        conn.commit()
        
        ticket_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return f"Complaint logged successfully into ticket management system! Ticket ID: #TKT-{ticket_id}"
    except Exception as e:
        return f"Failed to record complaint: {str(e)}"