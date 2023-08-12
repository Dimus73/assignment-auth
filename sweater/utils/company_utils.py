from sweater import db
from sweater.models.company_model import Company, CompanyMembers


def is_company_in_db(user_id, company):
    candidate = Company.query.filter_by(owner_id=user_id, name=company).first()
    return True if candidate else False


def create_company (user_id, company):
    new_company = Company(owner_id=user_id, name=company)
    db.session.add(new_company)
    db.session.commit()


def is_user_in_company (user_id, company_id):
    candidate = CompanyMembers.query.filter_by(company_id=company_id, user_id=user_id).first()
    return True if candidate else False


def add_user_to_company(user_id, company_id):
    new_in_company = CompanyMembers(company_id=company_id, user_id=user_id)
    db.session.add(new_in_company)
    db.session.commit()

