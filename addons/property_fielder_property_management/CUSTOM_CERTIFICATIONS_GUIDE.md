# Custom Certification Types - User Guide

## Overview

The Property Fielder Property Management addon allows you to create **custom certification types** beyond the pre-configured FLAGE+ certifications. This enables you to track any property compliance requirement specific to your business needs.

---

## 🎯 What You Can Create

You can create custom certifications for:

### Building Services
- ✅ Boiler Service Certificate
- ✅ Lift Inspection Certificate
- ✅ CCTV Maintenance
- ✅ Door Entry System Service
- ✅ Burglar Alarm Service

### Safety & Compliance
- ✅ Fire Extinguisher Service
- ✅ Emergency Lighting Test
- ✅ Playground Safety Inspection

### Maintenance
- ✅ Gutter Cleaning
- ✅ Roof Inspection
- ✅ Drainage System Check
- ✅ Water Tank Cleaning

### Any Other Requirement
- ✅ Custom certifications with configurable validity periods
- ✅ Custom inspection frequencies
- ✅ Custom compliance requirements

---

## 📝 How to Create Custom Certification Types

### Method 1: Quick Create Wizard (Recommended)

The easiest way to create common certification types:

1. **Navigate to:**
   ```
   Property Management › Configuration › Quick Create Certification Type
   ```

2. **Select a template:**
   - Choose from 12 pre-configured templates
   - Or select "Custom Certification" to start from scratch

3. **Review auto-filled details:**
   - Name, Code, Description
   - FLAGE+ Category
   - Validity Period (days)
   - Warning Period (days)

4. **Customize if needed:**
   - Modify any field to match your requirements
   - Adjust validity and warning periods

5. **Click "Create"**
   - The certification type is created
   - You're taken to the full form to add requirements

### Method 2: Manual Creation

For full control over all settings:

1. **Navigate to:**
   ```
   Property Management › Configuration › Certification Types
   ```

2. **Click "Create"**

3. **Fill in Basic Information:**
   - **Name:** e.g., "Boiler Service Certificate"
   - **Code:** e.g., "BOILER" (must be unique, uppercase recommended)
   - **FLAGE+ Category:** Select appropriate category or "Other"
   - **Sequence:** Display order (lower numbers appear first)

4. **Configure Validity:**
   - **Validity Period:** Number of days the certification is valid
     - Examples: 365 (annual), 180 (bi-annual), 1825 (5 years)
   - **Warning Period:** Days before expiry to show warning
     - Examples: 30, 60, 90 days

5. **Add Description:**
   - Describe what the certification covers
   - Include legal requirements if applicable

6. **Add Compliance Requirements** (optional):
   - Click "Add a line" in the Requirements tab
   - Define specific inspection tasks
   - Set inspection frequency
   - Add legal references
   - Mark as mandatory or optional

7. **Save**

---

## 🔧 Configuration Options

### FLAGE+ Categories

| Category | When to Use |
|----------|-------------|
| **Fire Safety** | Fire-related certifications (extinguishers, alarms, emergency lighting) |
| **Legionella** | Water system certifications (tank cleaning, temperature checks) |
| **Asbestos** | Asbestos-related certifications |
| **Gas Safety** | Gas-related certifications (boiler service, gas appliances) |
| **Electrical** | Electrical certifications (alarm systems, CCTV) |
| **Other** | All other certifications (lifts, playgrounds, gutters, etc.) |

### Validity Period Examples

| Frequency | Days | Use For |
|-----------|------|---------|
| Monthly | 30 | Frequent checks (e.g., water temperature) |
| Quarterly | 90 | Quarterly inspections |
| Bi-annual | 180 | 6-monthly checks (e.g., lifts, gutters) |
| Annual | 365 | Most common (boilers, fire extinguishers, alarms) |
| 2 Years | 730 | Legionella risk assessments |
| 5 Years | 1825 | Electrical inspections (EICR) |
| 10 Years | 3650 | Energy Performance Certificates (EPC) |
| Custom | Any | Set your own period |

### Warning Period Recommendations

| Validity Period | Recommended Warning |
|-----------------|---------------------|
| 30-90 days | 7-14 days |
| 180 days | 30 days |
| 365 days | 30-60 days |
| 730+ days | 60-90 days |
| 1825+ days | 90-180 days |

---

## 📋 Pre-configured Templates

The Quick Create Wizard includes these templates:

| Template | Code | Validity | Category | Description |
|----------|------|----------|----------|-------------|
| **Boiler Service** | BOILER | 365 days | Gas | Annual boiler service and safety check |
| **Lift Inspection** | LIFT | 180 days | Other | 6-monthly lift safety inspection (LOLER) |
| **Fire Extinguisher** | FIRE_EXT | 365 days | Fire | Annual fire extinguisher inspection |
| **Emergency Lighting** | EMERG_LIGHT | 365 days | Fire | Annual emergency lighting test |
| **Water Tank Cleaning** | WATER_TANK | 365 days | Legionella | Annual water tank cleaning |
| **Playground Safety** | PLAYGROUND | 365 days | Other | Annual playground equipment inspection |
| **CCTV Maintenance** | CCTV | 365 days | Other | Annual CCTV system maintenance |
| **Gutter Cleaning** | GUTTER | 180 days | Other | Bi-annual gutter cleaning |
| **Roof Inspection** | ROOF | 365 days | Other | Annual roof condition inspection |
| **Drainage Check** | DRAINAGE | 365 days | Other | Annual drainage system inspection |
| **Burglar Alarm** | ALARM | 365 days | Other | Annual burglar alarm service |
| **Door Entry System** | DOOR_ENTRY | 365 days | Other | Annual door entry maintenance |

---

## 🎨 Adding Compliance Requirements

For each certification type, you can define specific requirements:

### Example: Boiler Service Certificate

1. **Requirement 1:**
   - Name: "Visual Inspection"
   - Mandatory: Yes
   - Frequency: Annual
   - Legal Reference: "Gas Safety (Installation and Use) Regulations 1998"

2. **Requirement 2:**
   - Name: "Flue Gas Analysis"
   - Mandatory: Yes
   - Frequency: Annual

3. **Requirement 3:**
   - Name: "Safety Device Testing"
   - Mandatory: Yes
   - Frequency: Annual

### Inspection Frequencies

- **Annual** - Once per year
- **Bi-Annual** - Twice per year (every 6 months)
- **Quarterly** - Four times per year (every 3 months)
- **Monthly** - Twelve times per year
- **Custom** - Specify custom frequency in days

---

## 💡 Best Practices

### Naming Conventions

✅ **Good:**
- "Boiler Service Certificate"
- "Lift Inspection (LOLER)"
- "Fire Extinguisher Annual Service"

❌ **Avoid:**
- "Boiler" (too vague)
- "Certificate" (not descriptive)
- "Thing 1" (not professional)

### Code Conventions

✅ **Good:**
- BOILER
- LIFT
- FIRE_EXT
- EMERG_LIGHT

❌ **Avoid:**
- boiler (use uppercase)
- Boiler Service (no spaces)
- BS (too short, unclear)

### Validity Periods

- ✅ Match legal requirements (e.g., Gas Safety = 365 days)
- ✅ Match manufacturer recommendations
- ✅ Consider seasonal factors (e.g., gutter cleaning before winter)
- ❌ Don't set too short (creates unnecessary work)
- ❌ Don't set too long (increases compliance risk)

### Warning Periods

- ✅ Allow enough time to schedule inspections
- ✅ Consider inspector availability
- ✅ Account for property access issues
- ❌ Don't set too short (may miss expiry)
- ❌ Don't set too long (too many false alarms)

---

## 🔄 Using Custom Certifications

Once created, custom certification types work exactly like FLAGE+ certifications:

1. **Add to Properties:**
   - Open a property
   - Go to Certifications tab
   - Add certification with your custom type

2. **Schedule Inspections:**
   - Create inspection
   - Select your custom certification type
   - Schedule and assign inspector

3. **Track Compliance:**
   - View on compliance dashboard
   - Receive expiry warnings
   - Generate compliance reports

4. **Renew Certifications:**
   - System tracks expiry dates
   - Shows "Expiring Soon" warnings
   - One-click renewal

---

## 📊 Examples by Industry

### Social Housing
- Boiler Service (annual)
- Lift Inspection (6-monthly)
- Fire Extinguisher Service (annual)
- Emergency Lighting (annual)
- Playground Safety (annual)

### Commercial Property
- CCTV Maintenance (annual)
- Door Entry System (annual)
- Burglar Alarm Service (annual)
- Roof Inspection (annual)
- Drainage Check (annual)

### Residential Lettings
- Boiler Service (annual)
- Gutter Cleaning (bi-annual)
- Water Tank Cleaning (annual)

---

## ❓ FAQ

**Q: Can I modify pre-configured FLAGE+ certifications?**
A: Yes, but it's recommended to keep them as-is for compliance. Create custom types for variations.

**Q: Can I delete a certification type?**
A: You can archive it (set Active = False), but deletion is only possible if no certifications use it.

**Q: Can I change the validity period after creating certifications?**
A: Yes, but it only affects new certifications. Existing ones keep their original expiry dates.

**Q: How many custom certification types can I create?**
A: Unlimited! Create as many as you need.

**Q: Can I export/import certification types?**
A: Yes, use Odoo's standard export/import functionality.

---

## 🚀 Quick Start Checklist

- [ ] Navigate to Configuration › Quick Create Certification Type
- [ ] Select a template or choose Custom
- [ ] Review and customize the details
- [ ] Click Create
- [ ] Add compliance requirements (optional)
- [ ] Add certification to a property
- [ ] Schedule an inspection
- [ ] Complete inspection and generate certificate

---

**You can now track any property compliance requirement with custom certification types!** 🎉

