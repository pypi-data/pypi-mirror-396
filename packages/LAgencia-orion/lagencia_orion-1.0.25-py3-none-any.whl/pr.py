from typing import List  # noqa: F401

from sqlalchemy.sql.expression import and_
from sqlalchemy import select
from orion.databases.config_db_empatia import get_session_empatia
from orion.databases.db_empatia.repositories.querys_searcher import NewRevenues, Property, Subscriptions

REAL_ESTATE= "castillo"

with get_session_empatia() as session:
    # Realizar la consulta
    result = (
        session.query(Subscriptions.id,
                      Property.code,
                      NewRevenues.price,
                      NewRevenues.old_price,
                      Subscriptions.mobile,
                      Subscriptions.token,
                      Subscriptions.week_noti,
                      Subscriptions.option,
                      Subscriptions.email,
                      NewRevenues.type_template,
                      Subscriptions.name,
                      Subscriptions.adviser_name,
                      Subscriptions.adviser_mobile
                      )
        .join(NewRevenues, NewRevenues.property_id == Property.id)
        .join(Subscriptions, Subscriptions.id == NewRevenues.subscription_id)
        .where(and_(Subscriptions.website == REAL_ESTATE,
                    Subscriptions.week_noti.isnot(None),
                    Subscriptions.send_match.is_(True),
                    NewRevenues.notified.is_(False),

        ))
        .all()
    )

print(result)
print(len(result))


