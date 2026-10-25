// Returns the company associated with the authenticated administrator.
function "Catalogo/authorize_admin" {
  input {
    int authenticated_user_id
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $input.authenticated_user_id
      output = ["id", "role", "account_id"]
    } as $user
  
    precondition ($user != null && $user.role == "admin" && $user.account_id != null) {
      error_type = "accessdenied"
      error = "An authenticated company administrator is required."
    }
  
    db.get account {
      field_name = "id"
      field_value = $user.account_id
      output = ["id"]
    } as $account
  
    precondition ($account != null) {
      error_type = "accessdenied"
      error = "The authenticated administrator has no valid company."
    }
  }

  response = $account.id
  guid = "uqMCVrkwT_bwsEiR50NdjxuwRFM"
}