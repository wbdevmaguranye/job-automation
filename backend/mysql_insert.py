cursor.execute("""
    INSERT INTO Jobs (title, company, url, description, date_posted)
    VALUES (%s, %s, %s, %s, %s)
""", ('DevOps Engineer', 'TechCorp', 'https://example.com', 'Job description here', '2025-01-06'))

connection.commit()
