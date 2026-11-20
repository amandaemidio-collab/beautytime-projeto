// Authenticate a platform administrator with email and password.
query "auth/platform/login" verb=POST {
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

    precondition ($user != null && $user.role == "platform_admin" && $user.account_id == null) {
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
        action    : "login_platform_admin"
        metadata  : {role: "platform_admin"}
      }
    } as $event_log
  }

  response = {
    authToken: $authToken
    user_id  : $user.id
    user_type: $user.role
  }
  guid = "oSTOsMa2F_95q6o3g6RrotDdR5w"
}
