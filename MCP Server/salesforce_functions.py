from simple_salesforce import Salesforce
import os, dotenv
from typing import Dict, Any

dotenv.load_dotenv()

def sfdc_connection():
    username = os.environ["SALESFORCE_USER"]
    password = os.environ["SALESFORCE_PASSWORD"]
    security_token = os.environ["SALESFORCE_TOKEN"]

    return Salesforce(
        username=username,
        password=password,
        security_token=security_token,
        client_id="Replit",
    )


def find_contact_or_lead_by_email(email):
    """
    Simplified function to find if an email belongs to a Contact or Lead in Salesforce.
    
    Args:
        email: Email address to search for (string)
    
    Returns:
        Dictionary with 'type' ('contact' or 'lead') and 'id', or None if not found
        Example: {'type': 'contact', 'id': '003XX000004TmiQYAS'}
        Example: {'type': 'lead', 'id': '00QXX000004TmiQYAS'}
        Example: None (if not found)
    """
    if not email or not email.strip():
        return None
    
    email = email.strip()
    
    # Get Salesforce connection
    sf = sfdc_connection()
    
    # First, check Contacts
    contact_query = f"SELECT Id, Email FROM Contact WHERE Email = '{email}' LIMIT 1"
    contacts = sf.query(contact_query)
    
    if contacts.get('records') and len(contacts['records']) > 0:
        contact = contacts['records'][0]
        return {
            'type': 'contact',
            'id': contact['Id']
        }
    
    # If not found as Contact, check Leads
    lead_query = f"SELECT Id, Email FROM Lead WHERE Email = '{email}' LIMIT 1"
    leads = sf.query(lead_query)
    
    if leads.get('records') and len(leads['records']) > 0:
        lead = leads['records'][0]
        return {
            'type': 'lead',
            'id': lead['Id']
        }
    
    # Not found in either
    return None

def update_lead_fields(lead_id: str, lead_fields: Dict[str, Any]) -> dict:
    """
    Update fields on an existing Lead.
    
    Args:
        lead_id: The Salesforce Lead Id to update
        lead_fields: Dictionary of field names and values to update on the lead
    
    Returns:
        dict: {'success': True, 'lead_id': lead_id} if successful, or error dict if failed
    """
    sf = sfdc_connection()
    
    # Update the lead with provided fields
    result = sf.Lead.update(lead_id, lead_fields)
    
    # simple-salesforce returns HTTP status code (204) on success, or a dict on error
    # Convert to consistent dict format
    if isinstance(result, dict):
        # Error case - return as is
        return result
    else:
        # Success case - wrap in dict
        return {
            'success': True,
            'lead_id': lead_id,
            'status_code': result
        }

def update_contact_fields(contact_id: str, contact_fields: Dict[str, Any]) -> dict:
    """
    Update fields on an existing Contact.
    
    Args:
        contact_id: The Salesforce Contact Id to update
        contact_fields: Dictionary of field names and values to update on the contact
    
    Returns:
        dict: {'success': True, 'contact_id': contact_id} if successful
    """
    sf = sfdc_connection()
    
    # Update the contact with provided fields
    result = sf.Contact.update(contact_id, contact_fields)
    
    # simple-salesforce returns HTTP status code (204) on success, or a dict on error
    # Convert to consistent dict format
    if isinstance(result, dict):
        # Error case - return as is
        return result
    else:
        # Success case - wrap in dict
        return {
            'success': True,
            'contact_id': contact_id,
            'status_code': result
        }

def create_lead(fields):
    sf = sfdc_connection()
    response = sf.Lead.create(fields)
    return response

def lookup_user_email(user_email: str) -> dict:
    """
    Lookup a User by email address and return user information.
    Args:
        user_email: User's email address
    Returns:
        dict containing the user's ID, email, name, title, and other info
    """
    sf = sfdc_connection()
    
    result = sf.query(f"SELECT Id, Email, Name, Title FROM User WHERE Email = '{user_email}' LIMIT 1")
    
    if result.get('records'):
        user = result['records'][0]
        return {
            "user_id": user.get('Id'),
            "name": user.get('Name'),
            "title": user.get('Title'),
            "success": True
        }
    else:
        return {
            "user_id": None,
            "name": None,
            "title": None,
            "success": False
        }