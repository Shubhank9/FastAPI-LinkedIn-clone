"""add institutions and link educations

Moves educations.institution (free text) to educations.institution_id
(foreign key to the new institutions table) without losing existing rows.

Legacy names are trimmed of leading/trailing whitespace, so "MIT" and
"  MIT " map to the same institution. Matching is otherwise exact
(case-sensitive); case-only variants are reported as a warning, not merged.

If any education row has a blank institution name, the migration stops
with an error and, because PostgreSQL DDL is transactional, nothing is
changed. Fix those rows and run the migration again.

Revision ID: f0ff45dd0cad
Revises: 3352f0ff59a9
Create Date: 2026-10-11 22:55:45.896620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0ff45dd0cad'
down_revision: Union[str, Sequence[str], None] = '3352f0ff59a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FK_NAME = "fk_educations_institution_id_institutions"

# legacy name with leading/trailing whitespace (spaces, tabs, newlines) removed
TRIMMED_LEGACY_NAME = r"regexp_replace(educations.institution, '^\s+|\s+$', '', 'g')"


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()

    # 1. institutions table
    op.create_table('institutions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_institutions_id'), 'institutions', ['id'], unique=False)

    # 2. temporary nullable column, filled in below
    op.add_column('educations', sa.Column('institution_id', sa.Integer(), nullable=True))

    # refuse to continue if a row has no usable name: we will not drop
    # the row or invent an institution for it
    blank_ids = conn.execute(sa.text(
        f"SELECT id FROM educations "
        f"WHERE educations.institution IS NULL OR {TRIMMED_LEGACY_NAME} = '' "
        f"ORDER BY id"
    )).scalars().all()
    if blank_ids:
        raise RuntimeError(
            "Migration aborted: educations with a blank institution name: "
            f"{blank_ids}. Set a real institution name on these rows and "
            "run the migration again. No changes were applied."
        )

    # 3 + 4. one institution per distinct trimmed legacy name
    conn.execute(sa.text(
        f"INSERT INTO institutions (name, created_at, updated_at) "
        f"SELECT DISTINCT {TRIMMED_LEGACY_NAME}, now(), now() FROM educations "
        f"ON CONFLICT (name) DO NOTHING"
    ))

    case_variants = conn.execute(sa.text(
        "SELECT string_agg(name, ' | ' ORDER BY name) FROM institutions "
        "GROUP BY lower(name) HAVING count(*) > 1"
    )).scalars().all()
    for variants in case_variants:
        print(f"WARNING: institutions differing only by case were kept separate: {variants}")

    # 5. point every education at its institution
    conn.execute(sa.text(
        f"UPDATE educations SET institution_id = institutions.id "
        f"FROM institutions WHERE institutions.name = {TRIMMED_LEGACY_NAME}"
    ))

    # 6. every row must be mapped before anything is dropped
    unmapped_ids = conn.execute(sa.text(
        "SELECT id FROM educations WHERE institution_id IS NULL ORDER BY id"
    )).scalars().all()
    if unmapped_ids:
        raise RuntimeError(
            f"Migration aborted: educations could not be mapped to an institution: "
            f"{unmapped_ids}. No changes were applied."
        )

    # 7. foreign key + index
    op.create_foreign_key(FK_NAME, 'educations', 'institutions', ['institution_id'], ['id'])
    op.create_index(op.f('ix_educations_institution_id'), 'educations', ['institution_id'], unique=False)

    # 8. now safe to require it
    op.alter_column('educations', 'institution_id', existing_type=sa.Integer(), nullable=False)

    # 9. legacy text column is no longer needed
    op.drop_column('educations', 'institution')


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    # restore the legacy text column from the linked institution names
    op.add_column('educations', sa.Column('institution', sa.String(length=255), nullable=True))
    conn.execute(sa.text(
        "UPDATE educations SET institution = institutions.name "
        "FROM institutions WHERE institutions.id = educations.institution_id"
    ))
    op.alter_column('educations', 'institution', existing_type=sa.String(length=255), nullable=False)

    op.drop_index(op.f('ix_educations_institution_id'), table_name='educations')
    op.drop_constraint(FK_NAME, 'educations', type_='foreignkey')
    op.drop_column('educations', 'institution_id')

    op.drop_index(op.f('ix_institutions_id'), table_name='institutions')
    op.drop_table('institutions')
