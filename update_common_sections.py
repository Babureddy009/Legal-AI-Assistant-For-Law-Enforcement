import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root1",
        password="pass",
        database="legal_ai"
    )

def update_section(cursor, section_number, punishment):
    cursor.execute("""
        UPDATE ipc_sections 
        SET punishment = %s 
        WHERE section_number = %s
    """, (punishment, section_number))

def main():
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Dictionary of common sections and their punishments
    common_sections = {
        "302": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
        "304": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
        "378": "Whoever, intending to take dishonestly any moveable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft. Punishment: Imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "379": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "420": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
        "376": "Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.",
        "307": "Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
        "323": "Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
        "324": "Whoever, except in the case provided for by section 334, voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which, used as a weapon of offence, is likely to cause death, or by means of fire or any heated substance, or by means of any poison or any corrosive substance, or by means of any explosive substance or by means of any substance which it is deleterious to the human body to inhale, to swallow, or to receive into the blood, or by means of any animal, shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "498A": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine."
    }
    
    # Update each section
    for section_number, punishment in common_sections.items():
        try:
            update_section(cursor, section_number, punishment)
            print(f"Updated Section {section_number}")
        except Exception as e:
            print(f"Error updating Section {section_number}: {str(e)}")
    
    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Update of common sections completed!")

if __name__ == "__main__":
    main() 