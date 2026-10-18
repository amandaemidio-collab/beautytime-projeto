// See account details
query "account/details" verb=GET {
  api_group = "Members & Accounts"
  auth = "user"

  input {
    // Unique identifier for the account
    int account_id
  }

  stack {
    precondition (false) {
      error_type = "accessdenied"
      error = "This public account-details endpoint is no longer available."
    }
  
    // Retrieve account details based on account ID
    db.get account {
      field_name = "id"
      field_value = $input.account_id
    } as $account_details
  }

  response = $account_details
  tags = ["xano:quick-start"]
  guid = "2nCEnIXcdcqS3zl9SHd3U8oj0a8"
}