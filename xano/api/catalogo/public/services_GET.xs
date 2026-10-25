// Returns only active public service fields for a company.
query "public/services" verb=GET {
  api_group = "Catalogo"

  input {
    text public_identifier filters=trim
  }

  stack {
    db.get account {
      field_name = "public_identifier"
      field_value = $input.public_identifier
      output = ["id"]
    } as $account
  
    precondition ($account != null) {
      error_type = "notfound"
      error = "Company not found."
    }
  
    db.query service {
      where = $db.service.account_id == $account.id && $db.service.is_active == true
      sort = {name: "asc"}
      return = {type: "list"}
    } as $services
  }

  response = ```
    $services|map:{
        name: $$.name,
        duration_minutes: $$.duration_minutes,
        price_cents: $$.price_cents
      }
    ```
  guid = "CtCJNvTaSwetL2bUfOxrY3SaUso"
}