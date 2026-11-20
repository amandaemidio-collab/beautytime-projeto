// Returns a salon and its services and professionals.
query "platform/accounts/{account_id}" verb=GET {
  api_group = "Platform"
  auth = "user"

  input {
    int account_id
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.get account {
      field_name = "id"
      field_value = $input.account_id
    } as $account

    precondition ($account != null) {
      error_type = "notfound"
      error = "Salon not found."
    }

    db.query service {
      where = $db.service.account_id == $account.id
      sort = {name: "asc"}
      return = {type: "list"}
    } as $services

    db.query professional {
      where = $db.professional.account_id == $account.id
      sort = {name: "asc"}
      return = {type: "list"}
    } as $professionals
  }

  response = {
    account: $account
    services: $services
    professionals: $professionals
  }
  guid = "DqBBkRMl7VDkgjPnA3oNaPo4Zfk"
}
