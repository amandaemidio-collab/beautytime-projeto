// Register a company administrator and company atomically.
query "auth/admin/signup" verb=POST {
  api_group = "Authentication"

  input {
    text name filters=trim
    email email filters=trim|lower
    text phone? filters=trim
    text password
    text company_name filters=trim
    text public_identifier
    text description? filters=trim
    text location? filters=trim
  }

  stack {
    var $identifier_matches {
      value = "/^[a-z0-9]+(-[a-z0-9]+)*$/"|regex_matches:$input.public_identifier
    }
  
    precondition ((($input.public_identifier|strlen) >= 3) && (($input.public_identifier|strlen) <= 40) && $identifier_matches) {
      error_type = "inputerror"
      error = "The public identifier must be 3 to 40 characters, using lowercase ASCII letters, digits and single hyphens only."
    }
  
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id"]
    } as $existing_user
  
    precondition ($existing_user == null) {
      error_type = "accessdenied"
      error = "This account is already in use."
    }
  
    db.get account {
      field_name = "public_identifier"
      field_value = $input.public_identifier
      output = ["id"]
    } as $existing_company
  
    precondition ($existing_company == null) {
      error_type = "inputerror"
      error = "This public identifier is already in use."
    }
  
    db.transaction {
      stack {
        db.add account {
          enforce_hidden_fields = false
          data = {
            name              : $input.company_name
            public_identifier: $input.public_identifier
            description       : $input.description
            location          : $input.location
          }
        } as $company
      
        db.add user {
          enforce_hidden_fields = false
          data = {
            name      : $input.name
            email     : $input.email
            phone     : $input.phone
            password  : $input.password
            account_id: $company.id
            role      : "admin"
          }
        } as $user
      
        function.run "Getting Started Template/create_event_log" {
          input = {
            user_id   : $user.id
            account_id: $company.id
            action    : "signup_admin"
            metadata  : {role: "admin", public_identifier: $company.public_identifier}
          }
        } as $event_log
      }
    }
  
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id", "role"]
    } as $created_user
  
    db.get account {
      field_name = "public_identifier"
      field_value = $input.public_identifier
      output = ["name", "public_identifier"]
    } as $created_company
  
    security.create_auth_token {
      table = "user"
      extras = {}
      expiration = 86400
      id = $created_user.id
    } as $authToken
  }

  response = {
    authToken: $authToken
    user_id  : $created_user.id
    user_type: $created_user.role
    company  : {
      name              : $created_company.name
      public_identifier: $created_company.public_identifier
    }
  }
  tags = ["xano:quick-start"]
  guid = "jGUb9ZxeXUpx7x-gJ3-rW47y7lY"
}
