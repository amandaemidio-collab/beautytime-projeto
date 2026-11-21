// Returns dashboard metrics for the authenticated salon administrator's account.
query "admin/dashboard" verb=GET {
  api_group = "Catalogo"
  auth = "user"

  input {
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    function.run "calculate_account_dashboard" {
      input = {account_id: $account_id}
    } as $dashboard
  }

  response = $dashboard
  guid = "rPg2cXZd5qVl1uM9ZMhkZB7Xlr8"
}
