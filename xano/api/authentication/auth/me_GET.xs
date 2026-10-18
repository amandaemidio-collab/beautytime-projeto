// Get the user record belonging to the authentication token
query "auth/me" verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "created_at", "name", "email", "phone", "account_id", "role"]
    } as $user
  
    precondition ($user != null) {
      error_type = "notfound"
      error = "Authenticated user not found."
    }
  
    precondition (($user.role == "client" && $user.account_id == null) || ($user.role == "admin" && $user.account_id != null)) {
      error_type = "accessdenied"
      error = "The authenticated account has an invalid identity or company association."
    }
  
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: $user.account_id
        action    : "get_auth_user"
        metadata  : {role: $user.role}
      }
    } as $event_log
  }

  response = $user
  tags = ["xano:quick-start"]
  guid = "R_7_R-8SS4-WfM3GS4ieMO0_vls"
}