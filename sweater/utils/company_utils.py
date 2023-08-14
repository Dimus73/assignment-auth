from sweater import db
from sweater.models.company_model import Company, CompanyMembers


def is_company_in_db(user_id, company):
    candidate = Company.query.filter_by(owner_id=user_id, name=company).first()
    return True if candidate else False


def create_company(user_id, company):
    new_company = Company(owner_id=user_id, name=company)
    db.session.add(new_company)
    db.session.commit()
    return get_owner_org_list(user_id)


def is_user_in_company (user_id, company_id):
    candidate = CompanyMembers.query.filter_by(company_id=company_id, user_id=user_id).first()
    return True if candidate else False


def add_user_to_company(user_id, company_id):
    new_in_company = CompanyMembers(company_id=company_id, user_id=user_id)
    db.session.add(new_in_company)
    db.session.commit()
    return


def get_owner_org_list(user_id):
    org_list_obj = Company.query.filter_by(owner_id=user_id).order_by(Company.name).all()
    org_list = [{'id': org.id, 'company':org.name} for org in org_list_obj]
    return org_list


def get_users_in_org(org_id):
    user_list_obj = CompanyMembers.query.filter_by(company_id=org_id)
    user_list = [{'id': user.member.id, 'email': user.member.email} for user in user_list_obj]
    return user_list


