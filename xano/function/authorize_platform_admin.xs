// Returns the authenticated platform administrator identity.
function "authorize_platform_admin" {
  input {
    int authenticated_user_id
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $input.authenticated_user_id
      output = ["id", "role", "account_id"]
    } as $user

    precondition ($user != null && $user.role == "platform_admin" && $user.account_id == null) {
      error_type = "accessdenied"
      error = "A platform administrator is required."
    }
  }
  response = $user.id
  guid = "80PbzTar_-qcMb1FeMFTF4GbDu4"
}
