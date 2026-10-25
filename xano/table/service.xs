// Stores services offered by a company.
table service {
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
    text name_key {
      visibility = "internal"
    }
  
    int duration_minutes
    int price_cents
    bool is_active?=true
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "account_id"}]}
    {
      type : "btree|unique"
      field: [{name: "account_id"}, {name: "name_key"}]
    }
  ]

  guid = "LgbZVQt-cnYclVvWApAxt6sJ4Ss"
}