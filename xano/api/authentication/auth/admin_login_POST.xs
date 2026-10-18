// Authenticate a company administrator with email and password.
query "auth/admin/login" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
    text password
  }

  stack {
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id", "name", "email", "password", "account_id", "role"]
    } as $user
  
    precondition ($user != null && $user.role == "admin" && $user.account_id != null) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    security.check_password {
      text_password = $input.password
      hash_password = $user.password
    } as $pass_result
  
    precondition ($pass_result) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }
  
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: $user.account_id
        action    : "login_admin"
        metadata  : {role: "admin"}
      }
    } as $event_log
  }

  response = {authToken: $authToken, user_id: $user.id, user_type: $user.role}
  tags = ["xano:quick-start"]
  guid = "AjlMrBAosV1Oc8JntHasNS8V0iU"
}
