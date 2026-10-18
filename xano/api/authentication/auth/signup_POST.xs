// Register a platform-wide client account and return an authentication token.
query "auth/signup" verb=POST {
  api_group = "Authentication"

  input {
    text name filters=trim
    email email filters=trim|lower
    text phone filters=trim
    text password
  }

  stack {
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $existing_user
  
    precondition ($existing_user == null) {
      error_type = "accessdenied"
      error = "This account is already in use."
    }
  
    db.add user {
      enforce_hidden_fields = false
      data = {
        name    : $input.name
        email   : $input.email
        phone   : $input.phone
        password: $input.password
        role    : "client"
      }
    } as $user
  
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
        action    : "signup_client"
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
  guid = "rUG4j5xdPgFjFGPIKXqnl6q3lKo"
}