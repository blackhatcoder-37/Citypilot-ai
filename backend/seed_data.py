"""
Seed script for CityPilot AI — PostgreSQL database.
Generates:
  - 20 departments
  - 5000 complaints
  - 365 weather records (one per day for a year)
  - 100 resources
  - 50 knowledge documents
"""
import random
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Add parent dir to path so imports work when run from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database.database import engine, SessionLocal, Base
from database.models import (
    Complaint, Weather, Resource, Department,
    ChatHistory, KnowledgeDocument,
    ComplaintCategory, Severity, ComplaintStatus,
    ResourceType, ResourceStatus,
)

# ── Configuration ──────────────────────────────────────────────────

WARDS = [f"Ward {i}" for i in range(1, 21)]  # 20 wards

CATEGORIES = list(ComplaintCategory)
SEVERITIES = list(Severity)
SEVERITY_WEIGHTS = [0.30, 0.35, 0.25, 0.10]

STATUSES = list(ComplaintStatus)
STATUS_WEIGHTS = [0.25, 0.30, 0.35, 0.10]

DEPARTMENT_DATA = [
    ("Water Department", "Rajesh Kumar", "water@citypilot.gov", 120),
    ("Sanitation", "Priya Sharma", "sanitation@citypilot.gov", 200),
    ("Traffic Police", "Amit Singh", "traffic@citypilot.gov", 350),
    ("Electrical Department", "Suresh Patel", "electrical@citypilot.gov", 85),
    ("Public Works", "Meena Gupta", "publicworks@citypilot.gov", 150),
    ("Health Services", "Dr. Anita Joshi", "health@citypilot.gov", 180),
    ("Fire Department", "Vikram Rao", "fire@citypilot.gov", 120),
    ("Municipal Engineering", "Deepak Verma", "engineering@citypilot.gov", 95),
    ("Urban Planning", "Kavita Reddy", "planning@citypilot.gov", 60),
    ("Disaster Management", "Sunil Nair", "disaster@citypilot.gov", 75),
    ("Parks and Recreation", "Neha Malhotra", "parks@citypilot.gov", 45),
    ("Building Inspection", "Rohit Saxena", "building@citypilot.gov", 55),
    ("Environmental Services", "Sunita Devi", "environment@citypilot.gov", 65),
    ("Transport Department", "Manoj Tiwari", "transport@citypilot.gov", 110),
    ("Revenue Department", "Lakshmi Iyer", "revenue@citypilot.gov", 80),
    ("Education Department", "Pooja Srivastava", "education@citypilot.gov", 90),
    ("Social Welfare", "Arjun Menon", "welfare@citypilot.gov", 70),
    ("IT Department", "Rahul Chopra", "it@citypilot.gov", 40),
    ("Legal Department", "Geeta Bhatia", "legal@citypilot.gov", 25),
    ("Finance Department", "Arun Kapoor", "finance@citypilot.gov", 50),
]

DESCRIPTIONS = {
    ComplaintCategory.FLOOD: [
        "Severe waterlogging reported on main road after heavy rainfall",
        "Basement flooding in residential area, water level rising",
        "Storm drain overflow causing street flooding near market area",
        "Underpass completely submerged, traffic diverted",
        "Flood water entering ground floor shops in commercial district",
    ],
    ComplaintCategory.GARBAGE: [
        "Garbage dump overflowing near residential colony, foul smell",
        "Municipal bins not cleared for 3 days, attracting stray animals",
        "Construction debris dumped illegally on public road",
        "Waste collection vehicle has not visited the area this week",
        "Open garbage burning reported near school premises",
    ],
    ComplaintCategory.TRAFFIC: [
        "Traffic signal malfunction at major intersection causing gridlock",
        "Heavy congestion due to road construction work without diversion",
        "Illegal parking blocking emergency vehicle access lane",
        "Pothole on highway causing accidents and traffic slowdown",
        "Missing road markings and signage near school zone",
    ],
    ComplaintCategory.WATER_LEAKAGE: [
        "Main water pipeline burst flooding entire street",
        "Continuous water leakage from overhead tank in public park",
        "Underground pipe crack causing low water pressure in colony",
        "Fire hydrant leaking water for past 48 hours, no action taken",
        "Water seepage damaging road surface and building foundation",
    ],
    ComplaintCategory.POWER_OUTAGE: [
        "Complete power failure in residential sector for over 6 hours",
        "Frequent power fluctuations damaging electronic appliances",
        "Transformer overload causing intermittent blackouts",
        "Exposed live wire hanging low near children playground",
        "Power outage affecting hospital backup generator running low",
    ],
    ComplaintCategory.STREET_LIGHT: [
        "Entire stretch of street lights non-functional on main boulevard",
        "Flickering street lights creating visibility hazard at night",
        "Newly installed LED lights already malfunctioning after one month",
        "Dark alley near bus stop posing safety risk for commuters",
        "Street light pole tilting dangerously after vehicle collision",
    ],
    ComplaintCategory.ROAD_DAMAGE: [
        "Large pothole on arterial road causing vehicle damage daily",
        "Road surface completely eroded after monsoon rains",
        "Speed breaker too high, scraping undercarriage of vehicles",
        "Manhole cover missing on busy street, pedestrian hazard",
        "Road caved in near drainage line, urgent repair needed",
    ],
    ComplaintCategory.MEDICAL_EMERGENCY: [
        "Ambulance response delayed due to traffic congestion in area",
        "Dengue outbreak reported, multiple cases in single ward",
        "Food poisoning cases from local restaurant, 15+ affected",
        "Senior citizen collapsed on road, nearest hospital 5km away",
        "Gas leak in industrial zone causing respiratory issues",
    ],
    ComplaintCategory.SEWAGE: [
        "Sewage overflow on main road creating health hazard",
        "Blocked drainage causing backflow into residential basements",
        "Septic tank overflow contaminating nearby water source",
        "Sewage treatment plant malfunction releasing untreated waste",
        "Open sewer line near food market attracting disease vectors",
    ],
}

RESOURCE_TYPE_ALLOCATIONS = [
    (ResourceType.GARBAGE_TRUCK, 20),
    (ResourceType.FIRE_TRUCK, 12),
    (ResourceType.AMBULANCE, 18),
    (ResourceType.WATER_PUMP, 15),
    (ResourceType.POLICE_VEHICLE, 20),
    (ResourceType.STAFF, 15),
]

RESOURCE_NAMES = {
    ResourceType.GARBAGE_TRUCK: ["GT-{:03d} Municipal Waste Carrier", "GT-{:03d} Compactor Unit", "GT-{:03d} Side Loader"],
    ResourceType.FIRE_TRUCK: ["FT-{:03d} Pumper Engine", "FT-{:03d} Aerial Ladder", "FT-{:03d} Rescue Unit"],
    ResourceType.AMBULANCE: ["AMB-{:03d} Basic Life Support", "AMB-{:03d} Advanced Life Support", "AMB-{:03d} Patient Transport"],
    ResourceType.WATER_PUMP: ["WP-{:03d} High Capacity Pump", "WP-{:03d} Submersible Unit", "WP-{:03d} Portable Dewatering"],
    ResourceType.POLICE_VEHICLE: ["PV-{:03d} Patrol Car", "PV-{:03d} Rapid Response", "PV-{:03d} Traffic Control"],
    ResourceType.STAFF: ["STAFF-{:03d} Field Inspector", "STAFF-{:03d} Emergency Responder", "STAFF-{:03d} Maintenance Crew"],
}

RESOURCE_STATUSES = list(ResourceStatus)
RESOURCE_STATUS_WEIGHTS = [0.50, 0.30, 0.15, 0.05]

WEATHER_CONDITIONS = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Heavy Rain", "Thunderstorm", "Foggy", "Hazy"]

KNOWLEDGE_DOC_TEMPLATES = [
    ("City_Emergency_Response_Protocol.pdf", "pdf"),
    ("Ward_Boundary_Map.pdf", "pdf"),
    ("Annual_Budget_Report_2025.xlsx", "xlsx"),
    ("Drainage_System_Blueprint.pdf", "pdf"),
    ("Traffic_Signal_Inventory.csv", "csv"),
    ("Water_Pipeline_Network.pdf", "pdf"),
    ("Monsoon_Preparedness_Plan.docx", "docx"),
    ("Street_Light_Maintenance_Log.xlsx", "xlsx"),
    ("Solid_Waste_Management_Policy.pdf", "pdf"),
    ("Public_Health_Guidelines.pdf", "pdf"),
    ("Road_Construction_Schedule.csv", "csv"),
    ("Fire_Safety_Compliance_Report.pdf", "pdf"),
    ("Urban_Development_Master_Plan.pdf", "pdf"),
    ("Citizen_Complaint_Analysis_Q1.xlsx", "xlsx"),
    ("Environmental_Impact_Assessment.pdf", "pdf"),
    ("Power_Grid_Topology_Map.pdf", "pdf"),
    ("Ambulance_Route_Optimization.docx", "docx"),
    ("Sewage_Treatment_Capacity_Report.pdf", "pdf"),
    ("Traffic_Flow_Analysis_2025.csv", "csv"),
    ("Disaster_Recovery_Playbook.pdf", "pdf"),
    ("Building_Code_Regulations.pdf", "pdf"),
    ("Garbage_Collection_Routes.csv", "csv"),
    ("Water_Quality_Test_Results.xlsx", "xlsx"),
    ("Air_Quality_Monitoring_Data.csv", "csv"),
    ("Smart_City_IoT_Sensor_Inventory.xlsx", "xlsx"),
    ("Parking_Facility_Usage_Report.pdf", "pdf"),
    ("Public_Transport_Ridership_Data.csv", "csv"),
    ("School_Zone_Safety_Audit.pdf", "pdf"),
    ("Hospital_Emergency_Capacity.xlsx", "xlsx"),
    ("Bridge_Inspection_Report.pdf", "pdf"),
    ("Flood_Zone_Mapping.pdf", "pdf"),
    ("Noise_Pollution_Survey.csv", "csv"),
    ("Green_Cover_Analysis.pdf", "pdf"),
    ("Property_Tax_Collection_Report.xlsx", "xlsx"),
    ("CCTV_Network_Status.csv", "csv"),
    ("Streetlight_Energy_Audit.pdf", "pdf"),
    ("Pothole_Tracking_Database.csv", "csv"),
    ("Rain_Water_Harvesting_Sites.pdf", "pdf"),
    ("COVID_Vaccination_Centers.xlsx", "xlsx"),
    ("E_Governance_Implementation.pdf", "pdf"),
    ("Citizen_Satisfaction_Survey_2025.pdf", "pdf"),
    ("Ward_Commissioner_Contact_List.csv", "csv"),
    ("Municipal_Tender_Documents.pdf", "pdf"),
    ("Tree_Census_Report.pdf", "pdf"),
    ("Stray_Animal_Census.xlsx", "xlsx"),
    ("Public_Toilet_Locations.csv", "csv"),
    ("Heritage_Building_Registry.pdf", "pdf"),
    ("Solar_Panel_Installation_Plan.pdf", "pdf"),
    ("Workforce_Attendance_Log.xlsx", "xlsx"),
    ("Annual_Maintenance_Contract_List.pdf", "pdf"),
]

# Base coordinates (roughly New Delhi, India)
BASE_LAT = 28.6139
BASE_LNG = 77.2090
SPREAD = 0.08  # ~8km spread

# Pre-defined ward center coordinates (spread around base)
WARD_COORDS = {
    f"Ward {i}": (
        round(BASE_LAT + (((i - 1) % 5) - 2) * 0.012, 4),
        round(BASE_LNG + (((i - 1) // 5) - 2) * 0.012, 4),
    )
    for i in range(1, 21)
}



def generate_departments(session):
    print(f"  Seeding {len(DEPARTMENT_DATA)} departments...")
    departments = []
    for name, head, email, staff in DEPARTMENT_DATA:
        departments.append(Department(
            name=name,
            head=head,
            contact_email=email,
            total_staff=staff,
        ))
    session.bulk_save_objects(departments)
    session.commit()
    print(f"  [OK] {len(DEPARTMENT_DATA)} departments seeded.")


def generate_complaints(session, count=5000):
    print(f"  Seeding {count} complaints...")
    now = datetime.now(timezone.utc)
    complaints = []
    dept_names = [d[0] for d in DEPARTMENT_DATA]

    for i in range(count):
        category = random.choice(CATEGORIES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS, k=1)[0]
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        ward = random.choice(WARDS)

        days_ago = random.randint(0, 365)
        created = now - timedelta(
            days=days_ago,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        resolution_hours = None
        if status == ComplaintStatus.RESOLVED:
            resolution_hours = round(random.uniform(0.5, 96), 1)

        complaints.append(Complaint(
            category=category,
            description=random.choice(DESCRIPTIONS[category]),
            ward=ward,
            severity=severity,
            status=status,
            lat=round(BASE_LAT + random.uniform(-SPREAD, SPREAD), 6),
            lng=round(BASE_LNG + random.uniform(-SPREAD, SPREAD), 6),
            created_at=created,
            updated_at=created + timedelta(hours=random.randint(0, 48)) if status != ComplaintStatus.OPEN else created,
            assigned_department=random.choice(dept_names),
            resolution_hours=resolution_hours,
        ))

        if (i + 1) % 1000 == 0:
            session.bulk_save_objects(complaints)
            session.commit()
            complaints = []
            print(f"    ... {i + 1}/{count}")

    if complaints:
        session.bulk_save_objects(complaints)
        session.commit()
    print(f"  [OK] {count} complaints seeded.")


def generate_weather(session, days=365):
    print(f"  Seeding {days} weather records...")
    now = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    records = []

    for day_offset in range(days):
        date = now - timedelta(days=days - 1 - day_offset)
        month = date.month

        # Seasonal temperature patterns (Indian climate)
        if month in (12, 1, 2):       # Winter
            temp = round(random.uniform(5, 22), 1)
            precip = round(random.uniform(0, 5), 1)
            condition = random.choices(
                ["Clear", "Foggy", "Hazy", "Partly Cloudy"],
                weights=[0.3, 0.35, 0.2, 0.15], k=1
            )[0]
        elif month in (3, 4, 5):      # Summer
            temp = round(random.uniform(28, 46), 1)
            precip = round(random.uniform(0, 2), 1)
            condition = random.choices(
                ["Clear", "Hazy", "Partly Cloudy", "Cloudy"],
                weights=[0.4, 0.3, 0.2, 0.1], k=1
            )[0]
        elif month in (6, 7, 8, 9):   # Monsoon
            temp = round(random.uniform(24, 36), 1)
            precip = round(random.uniform(0, 120), 1)
            condition = random.choices(
                ["Heavy Rain", "Thunderstorm", "Light Rain", "Cloudy", "Partly Cloudy"],
                weights=[0.25, 0.15, 0.25, 0.20, 0.15], k=1
            )[0]
        else:                          # Post-monsoon
            temp = round(random.uniform(15, 32), 1)
            precip = round(random.uniform(0, 15), 1)
            condition = random.choices(
                ["Clear", "Partly Cloudy", "Hazy", "Light Rain"],
                weights=[0.35, 0.30, 0.20, 0.15], k=1
            )[0]

        humidity = round(random.uniform(20, 95), 1)
        wind = round(random.uniform(2, 45), 1)
        aqi = random.randint(30, 450)

        records.append(Weather(
            recorded_at=date,
            temperature_c=temp,
            humidity_pct=humidity,
            precipitation_mm=precip,
            wind_speed_kmh=wind,
            condition=condition,
            aqi=aqi,
        ))

    session.bulk_save_objects(records)
    session.commit()
    print(f"  [OK] {days} weather records seeded.")


def generate_resources(session, count=100):
    print(f"  Seeding {count} resources...")
    resources = []
    now = datetime.now(timezone.utc)
    idx = 0

    for rtype, allocation in RESOURCE_TYPE_ALLOCATIONS:
        for i in range(allocation):
            if idx >= count:
                break
            name_template = random.choice(RESOURCE_NAMES[rtype])
            status = random.choices(RESOURCE_STATUSES, weights=RESOURCE_STATUS_WEIGHTS, k=1)[0]
            ward = random.choice(WARDS)

            last_deployed = None
            if status == ResourceStatus.DEPLOYED:
                last_deployed = now - timedelta(hours=random.randint(0, 48))
            elif status in (ResourceStatus.MAINTENANCE, ResourceStatus.AVAILABLE):
                last_deployed = now - timedelta(days=random.randint(1, 30))

            resources.append(Resource(
                type=rtype,
                name=name_template.format(idx + 1),
                status=status,
                ward=ward,
                lat=round(BASE_LAT + random.uniform(-SPREAD, SPREAD), 6),
                lng=round(BASE_LNG + random.uniform(-SPREAD, SPREAD), 6),
                last_deployed=last_deployed,
            ))
            idx += 1

    session.bulk_save_objects(resources)
    session.commit()
    print(f"  [OK] {idx} resources seeded.")


def generate_knowledge_documents(session, count=50):
    print(f"  Seeding {count} knowledge documents...")
    now = datetime.now(timezone.utc)
    docs = []

    for i in range(min(count, len(KNOWLEDGE_DOC_TEMPLATES))):
        original_filename, file_type = KNOWLEDGE_DOC_TEMPLATES[i]
        stored_filename = f"{uuid.uuid4().hex}.{file_type}"

        docs.append(KnowledgeDocument(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size_bytes=random.randint(10_000, 5_000_000),
            file_path=f"uploads/{stored_filename}",
            upload_date=now - timedelta(days=random.randint(0, 180)),
            status="Uploaded",
            is_embedded=random.choice([True, False]),
        ))

    session.bulk_save_objects(docs)
    session.commit()
    print(f"  [OK] {len(docs)} knowledge documents seeded.")


def main():
    print("=" * 60)
    print("  CityPilot AI — PostgreSQL Database Seeder")
    print("=" * 60)

    # Create all tables
    print("\n-> Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tables created.\n")

    session = SessionLocal()
    try:
        # Check if data already exists
        existing = session.query(Complaint).count()
        if existing > 0:
            print(f"  [!] Database already has {existing} complaints.")
            resp = input("  Drop and re-seed? (y/N): ").strip().lower()
            if resp != "y":
                print("  Aborted.")
                return
            print("  Dropping existing data...")
            session.query(KnowledgeDocument).delete()
            session.query(ChatHistory).delete()
            session.query(Resource).delete()
            session.query(Weather).delete()
            session.query(Complaint).delete()
            session.query(Department).delete()
            session.commit()

        generate_departments(session)
        generate_complaints(session, 5000)
        generate_weather(session, 365)
        generate_resources(session, 100)
        generate_knowledge_documents(session, 50)

        print("\n" + "=" * 60)
        print("  [OK] Seeding complete!")
        print(f"    Departments:      {session.query(Department).count()}")
        print(f"    Complaints:       {session.query(Complaint).count()}")
        print(f"    Weather:          {session.query(Weather).count()}")
        print(f"    Resources:        {session.query(Resource).count()}")
        print(f"    Knowledge Docs:   {session.query(KnowledgeDocument).count()}")
        print("=" * 60)
    except Exception as e:
        session.rollback()
        print(f"\n  [ERROR] {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
