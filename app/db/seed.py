from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.skill import Skill


COMPANIES = [
    "Google",
    "Microsoft",
    "Amazon",
    "Meta",
    "Apple",
    "OpenAI",
    "Infosys",
    "TCS",
    "Wipro",
    "Accenture",
]


SKILLS = [
    "JavaScript",
    "TypeScript",
    "React",
    "Next.js",
    "Python",
    "FastAPI",
    "PostgreSQL",
    "MongoDB",
    "Docker",
    "Git",
]


def seed_companies(db):
    for company_name in COMPANIES:
        existing_company = db.scalar(
            select(Company).where(
                Company.name == company_name
            )
        )

        if not existing_company:
            db.add(
                Company(name=company_name)
            )


def seed_skills(db):
    for skill_name in SKILLS:
        existing_skill = db.scalar(
            select(Skill).where(
                Skill.name == skill_name
            )
        )

        if not existing_skill:
            db.add(
                Skill(name=skill_name)
            )


def run_seed():
    db = SessionLocal()

    try:
        seed_companies(db)
        seed_skills(db)

        db.commit()

        print("Seed data inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()