# Gmail Service Account Setup Instructions

This guide will help you create a Google Service Account with the necessary permissions to send emails via Gmail API.

## Prerequisites

- A Google Cloud Platform (GCP) account
- Access to Google Workspace Admin Console (if using domain-wide delegation)
- The email domain you want to send emails from must be in Google Workspace

## Step-by-Step Instructions

### Step 1: Create or Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Either:
   - Select an existing project, OR
   - Click "New Project" and create a new one
   - Give it a name (e.g., "Gmail Service Account")
   - Click "Create"

### Step 2: Enable Gmail API

1. In your Google Cloud Project, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" from the results
4. Click **"Enable"**

### Step 3: Create a Service Account

1. Go to **APIs & Services** > **Credentials**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"Service account"**
4. Fill in the details:
   - **Service account name**: `gmail-sender` (or any name you prefer)
   - **Service account ID**: Will auto-populate
   - **Description**: "Service account for sending emails via Gmail API"
5. Click **"CREATE AND CONTINUE"**
6. Skip the optional steps (Grant access, Grant users access) and click **"DONE"**

### Step 4: Create and Download the Service Account Key

1. In the **Credentials** page, find your newly created service account
2. Click on the service account email address
3. Go to the **"Keys"** tab
4. Click **"ADD KEY"** > **"Create new key"**
5. Select **"JSON"** as the key type
6. Click **"CREATE"**
7. The JSON file will automatically download - **save this file securely!**
8. Update the code to match the JSON file name:
   - Place it in: `MCP Server/` directory

### Step 5: Enable Domain-Wide Delegation (Required for Gmail)

Since your code uses `with_subject(user_email)`, you need domain-wide delegation:

1. Still in the service account details page, note the **"Unique ID"** (looks like: `123456789012345678901`)
2. Go to [Google Workspace Admin Console](https://admin.google.com/)
3. Navigate to **Security** > **API Controls** > **Domain-wide Delegation**
4. Click **"Add new"**
5. Fill in:
   - **Client ID**: The Unique ID from Step 5.1
   - **OAuth Scopes**: 
     ```
     https://www.googleapis.com/auth/gmail.send
     ```
   - **Client name**: `Gmail Service Account` (or any descriptive name)
6. Click **"Authorize"**

### Step 6: Verify Service Account Permissions

1. In Google Cloud Console, go back to your service account
2. Under **"Details"**, verify:
   - Service account email is listed
   - The service account has the Gmail API enabled
   - Domain-wide delegation is enabled (you'll see a note if it is)

### Step 7: Place the JSON File in Your Project

1. Move the downloaded JSON file to your project:
   ```
   MCP Server/inbound-footing-412823-c2ffc4659d84.json
   ```
   
   update `gmail_functions.py` line 10 to match your filename:
   ```python
   SERVICE_ACCOUNT_FILE = os.path.join(SCRIPT_DIR, 'your-filename.json')
   ```

### Step 8: Test the Setup

You can test if everything works by running:

```python
from gmail_functions import get_gmail_service

# Replace with an email from your Google Workspace domain
service = get_gmail_service("user@yourdomain.com")
print("Service account configured successfully!")
```

## Important Notes

⚠️ **Security Considerations:**
- **Never commit the JSON file to git** (it's already in `.gitignore`)
- Store the JSON file securely
- The service account has access to send emails on behalf of any user in your domain
- Keep the JSON file private and secure

⚠️ **Permissions:**
- The service account needs domain-wide delegation enabled
- The user email you pass to `get_gmail_service()` must be from your Google Workspace domain
- The user must exist in your Google Workspace

⚠️ **Limits:**
- Gmail API has daily sending limits (varies by account type)
- Free Google accounts: 500 emails/day
- Google Workspace: Higher limits depending on your plan

## Troubleshooting

**Error: "Invalid credentials"**
- Verify the JSON file path is correct
- Check that the JSON file is valid JSON
- Ensure the service account exists in GCP

**Error: "Insufficient permissions"**
- Verify domain-wide delegation is set up correctly
- Check that the OAuth scope matches exactly: `https://www.googleapis.com/auth/gmail.send`
- Ensure the Client ID in Admin Console matches the service account's Unique ID

**Error: "User not found" or "Delegation denied"**
- Verify the email address is from your Google Workspace domain
- Check that domain-wide delegation is properly configured
- Wait a few minutes after setting up delegation (it can take time to propagate)

## Additional Resources

- [Google Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Domain-Wide Delegation Guide](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority)

