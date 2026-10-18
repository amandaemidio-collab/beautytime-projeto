// Authenticate a client account with email and password.
query "auth/login" verb=POST {
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
  
    precondition ($user != null && $user.role == "client" && $user.account_id == null) {
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
        account_id: null
        action    : "login_client"
        metadata  : {role: "client"}
      }
    } as $event_log
  }

  response = {
    authToken: $authToken
    user_id  : $user.id
    user_type: $user.role
  }

  tags = ["xano:quick-start"]
  guid = "g6E8E2wr8FPWccUg-4Qqxu2csFg"
}