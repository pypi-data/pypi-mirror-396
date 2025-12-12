# from sqlalchemy import and_
# from xll_kit.core.permission.registry import permission_registry
# from models import User
#
# # rule: function(stmt, user_context) -> stmt
# def user_data_scope(stmt, user_ctx):
#     """
#     例如：只允许查看同一个 department 的 User
#     """
#     if user_ctx is None:
#         return stmt
#
#     dept_id = getattr(user_ctx, "dept_id", None)
#     if dept_id:
#         stmt = stmt.where(User.department_id == dept_id)
#
#     return stmt
#
#
# permission_registry.register("User", user_data_scope)
