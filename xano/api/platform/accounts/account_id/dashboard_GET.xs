// Returns salon dashboard metrics for the current Sao Paulo day and week.
query "platform/accounts/{account_id}/dashboard" verb=GET {
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
      output = ["id"]
    } as $account

    precondition ($account != null) {
      error_type = "notfound"
      error = "Salon not found."
    }

    function.run "calculate_account_dashboard" {
      input = {account_id: $account.id}
    } as $dashboard
  }

  response = $dashboard
  guid = "A2dgiW4jZr5ZHY-9lC2wowheDSg"
}
