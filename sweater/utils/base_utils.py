from sweater.models.auth_model import User


def is_id_in_model(id, model):
    candidate = model.query.filter_by(id=id).first()
    return True if candidate else False

# def is_user_in_db(user_id):
#     candidate = User.query.filter_by(id=user_id).first()
#     return True if candidate else False
