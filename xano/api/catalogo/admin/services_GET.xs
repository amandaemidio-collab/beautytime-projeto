// Lists the authenticated administrator's company and service catalog.
query "admin/services" verb=GET {
  api_group = "Catalogo"
  auth = "user"

  input {
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    db.get account {
      field_name = "id"
      field_value = $account_id
      output = ["name", "public_identifier"]
    } as $account

    db.query service {
      where = $db.service.account_id == $account_id
      sort = {name: "asc"}
      return = {type: "list"}
    } as $services
  }

  response = {
    company: $account
    services: $services|map:{
      id: $$.id,
      name: $$.name,
      duration_minutes: $$.duration_minutes,
      price_cents: $$.price_cents,
      is_active: $$.is_active
    }
  }
  guid = "bM1ZIsANbc5XxwIMqRog7x7zQ28"
}
