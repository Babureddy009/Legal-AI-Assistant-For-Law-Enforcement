print("FIR API loaded!")
from fastapi import APIRouter, HTTPException, Depends, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
import json
from config import get_db_config
import os
from fastapi.security.api_key import APIKeyHeader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import tempfile

router = APIRouter()

API_KEY = os.environ.get('API_KEY', 'changeme')
API_KEY_NAME = 'X-API-Key'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=401, detail='Invalid or missing API Key')

# Update CORS to use env var
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')

# Mount static files and templates
templates = Jinja2Templates(directory="static")

# Pydantic models for request validation
class ComplainantDetails(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(..., regex='^(Male|Female|Other)$')
    nationality: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    address: str = Field(..., min_length=1)
    contact: str = Field(..., min_length=1, max_length=100)

class FIRSubmission(BaseModel):
    police_station: str = Field(..., min_length=1, max_length=100)
    fir_number: Optional[str] = Field(None, max_length=50)
    district: str = Field(..., min_length=1, max_length=100)
    fir_date: date
    complainant: ComplainantDetails
    info_type: str = Field(..., regex='^(Oral|Written)$')
    place_of_occurrence: str = Field(..., min_length=1)
    date_time_of_occurrence: datetime
    accused_details: Optional[str] = None
    property_details: Optional[str] = None
    property_value: Optional[float] = None
    complaint: str = Field(..., min_length=1)
    sections_acts: Optional[str] = None

# Pydantic models for IPC sections
class IPCSection(BaseModel):
    section_number: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    punishment: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class IPCSectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    punishment: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

def get_db_connection():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@router.get("/fir", response_class=HTMLResponse)
async def fir_form_page(request: Request):
    return templates.TemplateResponse("fir.html", {"request": request})

@router.post("/fir", tags=["FIR"])
async def submit_fir(fir_data: FIRSubmission):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert complainant details
        cursor.execute("""
            INSERT INTO fir_complainants 
            (name, parent_name, age, gender, nationality, occupation, address, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fir_data.complainant.name,
            fir_data.complainant.parent_name,
            fir_data.complainant.age,
            fir_data.complainant.gender,
            fir_data.complainant.nationality,
            fir_data.complainant.occupation,
            fir_data.complainant.address,
            fir_data.complainant.contact
        ))
        complainant_id = cursor.lastrowid

        # Insert FIR report
        cursor.execute("""
            INSERT INTO fir_reports 
            (fir_number, police_station, district, fir_date, complainant_id,
             info_type, place_of_occurrence, date_time_of_occurrence,
             accused_details, property_details, property_value,
             complaint, sections_acts, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted')
        """, (
            fir_data.fir_number,
            fir_data.police_station,
            fir_data.district,
            fir_data.fir_date,
            complainant_id,
            fir_data.info_type,
            fir_data.place_of_occurrence,
            fir_data.date_time_of_occurrence,
            fir_data.accused_details,
            fir_data.property_details,
            fir_data.property_value,
            fir_data.complaint,
            fir_data.sections_acts
        ))
        
        fir_id = cursor.lastrowid
        connection.commit()

        return {
            "status": "success",
            "message": "FIR submitted successfully",
            "fir_id": fir_id,
            "complainant_id": complainant_id
        }

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/fir/search")
async def search_fir(request: Request):
    print("Search FIR endpoint called")  # Debug log
    try:
        params = dict(request.query_params)
        print(f"Query params: {params}")  # Debug log
        
        connection = None
        try:
            print("Connecting to database...")  # Debug log
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM fir_report_details WHERE 1=1"
            params_list = []

            # Handle search parameters
            police_station = params.get("police_station")
            district = params.get("district")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            status = params.get("status")

            if police_station:
                query += " AND police_station LIKE %s"
                params_list.append(f"%{police_station}%")
            if district:
                query += " AND district LIKE %s"
                params_list.append(f"%{district}%")
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    query += " AND fir_date >= %s"
                    params_list.append(start_date_obj)
                except Exception:
                    pass
            if end_date:
                try:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    query += " AND fir_date <= %s"
                    params_list.append(end_date_obj)
                except Exception:
                    pass
            if status:
                query += " AND status = %s"
                params_list.append(status)

            print(f"Executing query: {query}")  # Debug log
            print(f"With params: {params_list}")  # Debug log
            cursor.execute(query, params_list)
            results = cursor.fetchall()
            print(f"Found {len(results)} results")  # Debug log

            # Convert datetime objects to strings
            for result in results:
                for key, value in result.items():
                    if isinstance(value, (datetime, date)):
                        result[key] = value.isoformat()

            # Format response for DataTables
            return {
                "draw": int(params.get("draw", 1)),
                "recordsTotal": len(results),
                "recordsFiltered": len(results),
                "data": results
            }

        except Error as e:
            print(f"Database error: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
                print("Database connection closed")  # Debug log
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/fir/{fir_id}")
async def get_fir(fir_id: int):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM fir_report_details WHERE id = %s
        """, (fir_id,))
        
        fir_data = cursor.fetchone()
        if not fir_data:
            raise HTTPException(status_code=404, detail="FIR not found")

        # Convert datetime objects to strings
        for key, value in fir_data.items():
            if isinstance(value, (datetime, date)):
                fir_data[key] = value.isoformat()

        return fir_data

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.put("/fir/{fir_id}/status", dependencies=[Security(get_api_key)])
async def update_fir_status(
    fir_id: int,
    status: str = Query(..., regex='^(Draft|Submitted|Under Review|Approved|Rejected)$')
):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE fir_reports 
            SET status = %s 
            WHERE id = %s
        """, (status, fir_id))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="FIR not found")

        connection.commit()
        return {"status": "success", "message": f"FIR status updated to {status}"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/fir/admin", response_class=HTMLResponse)
async def fir_admin_page(request: Request):
    return templates.TemplateResponse("fir_admin.html", {"request": request})

@router.delete("/fir/{fir_id}", dependencies=[Security(get_api_key)])
async def delete_fir(fir_id: int):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First get the complainant_id
        cursor.execute("SELECT complainant_id FROM fir_reports WHERE id = %s", (fir_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="FIR not found")
        
        complainant_id = result[0]

        # Delete the FIR report
        cursor.execute("DELETE FROM fir_reports WHERE id = %s", (fir_id,))
        
        # Delete the complainant
        cursor.execute("DELETE FROM fir_complainants WHERE id = %s", (complainant_id,))
        
        connection.commit()
        return {"status": "success", "message": "FIR deleted successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.put("/fir/{fir_id}", dependencies=[Security(get_api_key)])
async def update_fir(fir_id: int, fir_data: FIRSubmission):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get the complainant_id
        cursor.execute("SELECT complainant_id FROM fir_reports WHERE id = %s", (fir_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="FIR not found")
        
        complainant_id = result[0]

        # Update complainant details
        cursor.execute("""
            UPDATE fir_complainants 
            SET name = %s, parent_name = %s, age = %s, gender = %s,
                nationality = %s, occupation = %s, address = %s, contact = %s
            WHERE id = %s
        """, (
            fir_data.complainant.name,
            fir_data.complainant.parent_name,
            fir_data.complainant.age,
            fir_data.complainant.gender,
            fir_data.complainant.nationality,
            fir_data.complainant.occupation,
            fir_data.complainant.address,
            fir_data.complainant.contact,
            complainant_id
        ))

        # Update FIR report
        cursor.execute("""
            UPDATE fir_reports 
            SET police_station = %s, district = %s, fir_date = %s,
                info_type = %s, place_of_occurrence = %s, date_time_of_occurrence = %s,
                accused_details = %s, property_details = %s, property_value = %s,
                complaint = %s, sections_acts = %s
            WHERE id = %s
        """, (
            fir_data.police_station,
            fir_data.district,
            fir_data.fir_date,
            fir_data.info_type,
            fir_data.place_of_occurrence,
            fir_data.date_time_of_occurrence,
            fir_data.accused_details,
            fir_data.property_details,
            fir_data.property_value,
            fir_data.complaint,
            fir_data.sections_acts,
            fir_id
        ))

        connection.commit()
        return {"status": "success", "message": "FIR updated successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# IPC Section endpoints
@router.get("/ipc")
async def get_ipc_sections(
    section_number: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM ipc_sections WHERE 1=1"
        params = []

        if section_number:
            query += " AND section_number LIKE %s"
            params.append(f"%{section_number}%")
        if category:
            query += " AND category = %s"
            params.append(category)
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)

        cursor.execute(query, params)
        sections = cursor.fetchall()

        return sections

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/ipc/{section_number}")
async def get_ipc_section(section_number: str):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM ipc_sections WHERE section_number = %s", (section_number,))
        section = cursor.fetchone()
        
        if not section:
            raise HTTPException(status_code=404, detail="IPC section not found")

        return section

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.post("/ipc", dependencies=[Security(get_api_key)])
async def create_ipc_section(section: IPCSection):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ipc_sections 
            (section_number, title, description, punishment, category, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            section.section_number,
            section.title,
            section.description,
            section.punishment,
            section.category,
            section.is_active
        ))
        
        connection.commit()
        return {"status": "success", "message": "IPC section created successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        if "unique_section" in str(e):
            raise HTTPException(status_code=400, detail="IPC section number already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.put("/ipc/{section_number}", dependencies=[Security(get_api_key)])
async def update_ipc_section(section_number: str, section: IPCSectionUpdate):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Build dynamic update query based on provided fields
        update_fields = []
        params = []
        
        if section.title is not None:
            update_fields.append("title = %s")
            params.append(section.title)
        if section.description is not None:
            update_fields.append("description = %s")
            params.append(section.description)
        if section.punishment is not None:
            update_fields.append("punishment = %s")
            params.append(section.punishment)
        if section.category is not None:
            update_fields.append("category = %s")
            params.append(section.category)
        if section.is_active is not None:
            update_fields.append("is_active = %s")
            params.append(section.is_active)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        query = f"""
            UPDATE ipc_sections 
            SET {', '.join(update_fields)}
            WHERE section_number = %s
        """
        params.append(section_number)

        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="IPC section not found")

        connection.commit()
        return {"status": "success", "message": "IPC section updated successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.delete("/ipc/{section_number}", dependencies=[Security(get_api_key)])
async def delete_ipc_section(section_number: str):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM ipc_sections WHERE section_number = %s", (section_number,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="IPC section not found")

        connection.commit()
        return {"status": "success", "message": "IPC section deleted successfully"}

    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/ipc_sections")
async def api_get_ipc_sections():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ipc_sections")
        sections = cursor.fetchall()
        return sections
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.post("/ipc_sections")
async def api_add_ipc_section(section: dict):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO ipc_sections (section_number, title, description, punishment)
            VALUES (%s, %s, %s, %s)
            """,
            (
                section.get("section_number"),
                section.get("title"),
                section.get("description"),
                section.get("punishment"),
            ),
        )
        connection.commit()
        return {"status": "success", "id": cursor.lastrowid}
    except Error as e:
        if connection:
            connection.rollback()
        if "unique_section" in str(e):
            raise HTTPException(status_code=400, detail="IPC section number already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.delete("/ipc_sections/{id}")
async def api_delete_ipc_section(id: int):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ipc_sections WHERE id = %s", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="IPC section not found")
        connection.commit()
        return {"status": "success", "message": "IPC section deleted successfully"}
    except Error as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/fir/{fir_id}/pdf")
async def generate_fir_pdf(fir_id: int):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get FIR details
        cursor.execute("""
            SELECT * FROM fir_report_details WHERE id = %s
        """, (fir_id,))
        
        fir_data = cursor.fetchone()
        if not fir_data:
            raise HTTPException(status_code=404, detail="FIR not found")

        # Create a temporary file for the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        # Create PDF
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(f"FIR Report #{fir_data['fir_number']}", title_style))
        elements.append(Spacer(1, 20))

        # Create data for the table
        data = [
            ["Police Station", fir_data.get('police_station', 'N/A')],
            ["District", fir_data.get('district', 'N/A')],
            ["FIR Date", fir_data.get('fir_date', 'N/A') if not isinstance(fir_data.get('fir_date', None), (datetime, date)) else fir_data.get('fir_date').strftime('%Y-%m-%d')],
            ["Information Type", fir_data.get('info_type', 'N/A')],
            ["Place of Occurrence", fir_data.get('place_of_occurrence', 'N/A')],
            ["Date & Time of Occurrence", fir_data.get('date_time_of_occurrence', 'N/A') if not isinstance(fir_data.get('date_time_of_occurrence', None), (datetime, date)) else fir_data.get('date_time_of_occurrence').strftime('%Y-%m-%d %H:%M')],
            ["Status", fir_data.get('status', 'N/A')],
            ["Complainant Name", fir_data.get('complainant_name', 'N/A')],
            ["Complainant Parent Name", fir_data.get('complainant_parent_name', 'N/A')],
            ["Complainant Age", str(fir_data.get('complainant_age', 'N/A'))],
            ["Complainant Gender", fir_data.get('complainant_gender', 'N/A')],
            ["Complainant Nationality", fir_data.get('complainant_nationality', 'N/A')],
            ["Complainant Occupation", fir_data.get('complainant_occupation', 'N/A')],
            ["Complainant Address", fir_data.get('complainant_address', 'N/A')],
            ["Complainant Contact", fir_data.get('complainant_contact', 'N/A')],
            ["Accused Details", fir_data.get('accused_details', 'N/A')],
            ["Property Details", fir_data.get('property_details', 'N/A')],
            ["Property Value", str(fir_data.get('property_value', 'N/A')) if fir_data.get('property_value', None) else 'N/A'],
            ["Complaint", fir_data.get('complaint', 'N/A')],
            ["Sections & Acts", fir_data.get('sections_acts', 'N/A')]
        ]

        # Create table
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)
        doc.build(elements)

        return FileResponse(
            temp_file.name,
            media_type='application/pdf',
            filename=f'FIR_{fir_data["fir_number"]}.pdf'
        )

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8080) 