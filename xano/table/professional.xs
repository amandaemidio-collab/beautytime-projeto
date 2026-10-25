// Stores professionals belonging to a company.
table professional {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    int account_id {
      table = "account"
      visibility = "private"
    }

    text name filters=trim
    bool is_active?=true
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "account_id"}]}
  ]
  guid = "cWZBlgZAAQQCJjyqnw-R_x_5Ip8"
}
