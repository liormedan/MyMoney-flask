from datetime import datetime
import firebase_admin
from firebase_admin import db

class User:
    def __init__(self, uid, email, first_name='', last_name=''):
        self.uid = uid
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.utcnow().isoformat()
        self.last_login = datetime.utcnow().isoformat()

    @staticmethod
    def create(uid, email, first_name='', last_name=''):
        """Create a new user in Firebase Database"""
        try:
            user_ref = db.reference(f'/users/{uid}')
            
            user_data = {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': datetime.utcnow().isoformat(),
                'last_login': datetime.utcnow().isoformat()
            }
            
            user_ref.set(user_data)
            return User(uid=uid, **user_data)
        except Exception as e:
            print(f"Error creating user in database: {e}")
            return None

    @staticmethod
    def get_by_id(uid):
        """Get user by ID from Firebase Database"""
        try:
            user_ref = db.reference(f'/users/{uid}')
            user_data = user_ref.get()
            
            if user_data:
                return User(
                    uid=uid,
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', '')
                )
            return None
        except Exception as e:
            print(f"Error getting user from database: {e}")
            return None

    def update_last_login(self):
        """Update user's last login time"""
        try:
            user_ref = db.reference(f'/users/{self.uid}')
            user_ref.update({
                'last_login': datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'uid': self.uid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'last_login': self.last_login
        }

class Transaction:
    def __init__(self, user_id, amount, category, description='', date=None, transaction_type='expense'):
        self.user_id = user_id
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date or datetime.utcnow().isoformat()
        self.transaction_type = transaction_type

    @staticmethod
    def create(user_id, amount, category, description='', date=None, transaction_type='expense'):
        """Create a new transaction in Firebase Database"""
        try:
            transactions_ref = db.reference(f'/users/{user_id}/transactions').push()
            
            transaction_data = {
                'amount': float(amount),
                'category': category,
                'description': description,
                'date': date or datetime.utcnow().isoformat(),
                'transaction_type': transaction_type
            }
            
            transactions_ref.set(transaction_data)
            return Transaction(user_id=user_id, **transaction_data)
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None

    @staticmethod
    def get_user_transactions(user_id):
        """Get all transactions for a user"""
        try:
            transactions_ref = db.reference(f'/users/{user_id}/transactions')
            transactions_data = transactions_ref.get()
            
            if not transactions_data:
                return []
                
            transactions = []
            for transaction_id, data in transactions_data.items():
                transaction = Transaction(
                    user_id=user_id,
                    amount=data['amount'],
                    category=data['category'],
                    description=data.get('description', ''),
                    date=data['date'],
                    transaction_type=data.get('transaction_type', 'expense')
                )
                transactions.append(transaction)
                
            return transactions
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []

    def to_dict(self):
        """Convert transaction object to dictionary"""
        return {
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date,
            'transaction_type': self.transaction_type
        }
