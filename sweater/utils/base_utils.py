from sweater.models.auth_model import User


def is_user_in_db(user_id):
    candidate = User.query.filter_by(id=user_id).first()
    return True if candidate else False
