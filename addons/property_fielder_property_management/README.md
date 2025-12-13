# Property Fielder Property Management

Comprehensive property management system with UK FLAGE+ certification compliance tracking for Odoo.

## 📋 Overview

This addon provides complete property portfolio management with automated tracking of UK statutory compliance requirements under the FLAGE+ framework:

- **F** - Fire Safety
- **L** - Legionella Control
- **A** - Asbestos Management
- **G** - Gas Safety
- **E** - Electrical Safety

## ✨ Features

### Property Management
- ✅ Property portfolio tracking
- ✅ Property details (type, bedrooms, bathrooms, floor area)
- ✅ Owner/landlord and tenant management
- ✅ GPS coordinates for field service integration
- ✅ Property status tracking (Active, Vacant, Maintenance)
- ✅ Multi-property support

### FLAGE+ Certification Tracking
- ✅ **Fire Safety Certificate** - Annual fire risk assessments
- ✅ **Legionella Risk Assessment** - Bi-annual water system checks
- ✅ **Asbestos Management Survey** - Annual asbestos surveys
- ✅ **Gas Safety Certificate (CP12)** - Annual gas safety checks
- ✅ **Electrical Installation Condition Report (EICR)** - 5-year electrical inspections
- ✅ **Energy Performance Certificate (EPC)** - 10-year energy ratings
- ✅ **Portable Appliance Testing (PAT)** - Annual electrical appliance testing

### Configurable Compliance
- ✅ Configurable validity periods for each certification type
- ✅ Configurable warning periods (expiry alerts)
- ✅ Custom inspection frequencies (annual, bi-annual, quarterly, monthly, custom)
- ✅ Compliance requirements with legal references
- ✅ Mandatory vs optional requirements

### Compliance Monitoring
- ✅ Real-time compliance status dashboard
- ✅ FLAGE+ status indicators per property
- ✅ Expiry date tracking with countdown
- ✅ Automatic status updates (Valid, Expiring Soon, Expired)
- ✅ Expired certification alerts
- ✅ Compliance reports

### Inspection Management
- ✅ Schedule property inspections
- ✅ Link inspections to field service jobs
- ✅ Track inspection status (Draft, Scheduled, In Progress, Completed, Failed)
- ✅ Record inspection results (Pass, Fail, Conditional)
- ✅ Capture findings and recommendations
- ✅ Attach inspection reports and photos
- ✅ Auto-generate certificates from passed inspections

### Field Service Integration
- ✅ Create field service jobs from inspections
- ✅ Assign inspectors to properties
- ✅ GPS-tracked job completion
- ✅ Mobile app support for inspectors

### Document Management
- ✅ Upload and store certificates
- ✅ Attach inspection reports
- ✅ Photo attachments
- ✅ Document templates for requirements

## 📦 Models

### 1. Property (`property_fielder.property`)
Main property model with:
- Basic information (name, type, bedrooms, bathrooms)
- Address and GPS coordinates
- Owner/landlord and tenant
- Status tracking
- FLAGE+ compliance status
- Certifications and inspections

### 2. Certification Type (`property_fielder.certification.type`)
Defines certification types with:
- Name and code (FIRE, GAS, ELECTRICAL, etc.)
- FLAGE+ category
- Validity period (configurable in days)
- Warning period (configurable in days)
- Compliance requirements

### 3. Property Certification (`property_fielder.property.certification`)
Tracks individual certificates with:
- Certificate number
- Issue and expiry dates
- Status (Valid, Expiring Soon, Expired)
- Inspector/certifier details
- Certificate file upload
- Days until expiry calculation
- Auto-renewal functionality

### 4. Compliance Requirement (`property_fielder.compliance.requirement`)
Defines requirements for each certification type:
- Requirement name and description
- Mandatory/optional flag
- Legal reference
- Inspection frequency
- Document requirements

### 5. Property Inspection (`property_fielder.property.inspection`)
Manages inspections with:
- Inspection scheduling
- Inspector assignment
- Status tracking
- Results (Pass/Fail/Conditional)
- Findings and recommendations
- Report and photo attachments
- Certificate generation
- Field service job integration

## 🔧 Configuration

### Certification Types (Pre-configured)

| Certification | Code | Validity | Warning | Legal Reference |
|--------------|------|----------|---------|-----------------|
| Fire Safety | FIRE | 365 days | 60 days | Regulatory Reform (Fire Safety) Order 2005 |
| Legionella | LEGIONELLA | 730 days | 90 days | Health and Safety at Work Act 1974, ACOP L8 |
| Asbestos | ASBESTOS | 365 days | 60 days | Control of Asbestos Regulations 2012 |
| Gas Safety (CP12) | GAS | 365 days | 30 days | Gas Safety (Installation and Use) Regulations 1998 |
| Electrical (EICR) | ELECTRICAL | 1825 days | 90 days | Electrical Safety Standards Regulations 2020 |
| EPC | EPC | 3650 days | 180 days | Energy Performance of Buildings Regulations 2012 |
| PAT | PAT | 365 days | 30 days | Electricity at Work Regulations 1989 |

### Customization

All certification types can be customized:
1. Navigate to **Property Management › Configuration › Certification Types**
2. Edit existing types or create new ones
3. Configure:
   - Validity period (days)
   - Warning period (days)
   - FLAGE+ category
   - Compliance requirements

## 📊 Compliance Dashboard

The compliance dashboard provides:
- Overview of all properties
- FLAGE+ status at a glance
- Expired certifications count
- Expiring soon alerts
- Filter by compliance status
- Group by property type, city, owner

## 🔔 Alerts & Notifications

Automatic alerts for:
- Certifications expiring soon (based on warning period)
- Expired certifications
- Overdue inspections
- Failed inspections requiring follow-up

## 🔗 Integration with Field Service

### Create Inspection Jobs
1. Open an inspection
2. Click "Create Field Service Job"
3. Job is created with:
   - Property address and GPS coordinates
   - Scheduled date from inspection
   - Inspector assignment
   - Job notes with inspection details

### Complete Inspections
1. Inspector completes field service job
2. Updates inspection status
3. Records results and findings
4. Uploads photos and reports
5. System auto-generates certificate if passed

## 📱 Mobile App Support

Inspectors can use the Property Fielder Inspector mobile app to:
- View assigned inspection jobs
- Navigate to property locations
- Check in/out with GPS tracking
- Capture photos with GPS tagging
- Record findings and notes
- Upload inspection reports
- Capture customer signatures

## 🚀 Installation

1. **Install addon:**
   ```bash
   # Copy addon to Odoo addons directory
   cp -r property_fielder_property_management /path/to/odoo/addons/
   
   # Update apps list in Odoo
   # Settings › Apps › Update Apps List
   
   # Install Property Fielder Property Management
   # Apps › Search "Property Fielder Property Management" › Install
   ```

2. **Dependencies:**
   - `base` - Odoo base module
   - `mail` - Messaging and activities
   - `web` - Web interface
   - `property_fielder_field_service` - Field service integration

3. **Data loaded on installation:**
   - 7 pre-configured certification types (FLAGE+ and others)
   - 12 compliance requirements with legal references
   - Sequences for properties and inspections

## 👥 User Roles

### Property User
- View properties
- View certifications
- View inspections
- View compliance status

### Property Manager
- All user permissions
- Create/edit/delete properties
- Create/edit/delete certifications
- Create/edit/delete inspections
- Manage compliance requirements
- Generate reports

## 📈 Reports

Available reports:
- Compliance status report
- Certificate expiry report
- Property portfolio report
- Inspection history report

## 🔐 Security

- Role-based access control (User, Manager)
- Record rules for data access
- Activity tracking and audit trail
- Document access control

## 📝 Usage Example

### Adding a New Property

1. Navigate to **Property Management › Properties**
2. Click **Create**
3. Fill in property details:
   - Name: "123 Main Street, Flat 4"
   - Type: Flat/Apartment
   - Address and GPS coordinates
   - Owner/landlord
   - Current tenant
4. Save

### Adding Certifications

1. Open property
2. Go to **Certifications** tab
3. Click **Add a line**
4. Select certification type (e.g., Gas Safety)
5. Enter:
   - Certificate number
   - Issue date
   - Expiry date (auto-calculated)
   - Inspector details
6. Upload certificate file
7. Save

### Scheduling an Inspection

1. Navigate to **Property Management › Inspections**
2. Click **Create**
3. Select:
   - Property
   - Certification type
   - Scheduled date
   - Inspector
4. Click **Create Field Service Job** (optional)
5. Save

### Completing an Inspection

1. Open inspection
2. Click **Start Inspection**
3. Complete inspection work
4. Record:
   - Result (Pass/Fail/Conditional)
   - Findings
   - Recommendations
5. Upload report and photos
6. Click **Complete Inspection**
7. If passed, click **Generate Certificate**

## 🛠️ Technical Details

- **Odoo Version:** 17.0+
- **Python Version:** 3.10+
- **Database:** PostgreSQL 15+
- **License:** LGPL-3

## 📞 Support

For issues and questions, contact Property Fielder support.

## 📄 License

LGPL-3

