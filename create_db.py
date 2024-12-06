from app import create_app, db
from app.models import Expense, Income

app = create_app()

with app.app_context():
    print("יוצר את בסיס הנתונים...")
    db.create_all()
    print("בסיס הנתונים נוצר בהצלחה!")
