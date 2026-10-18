// Stores client and company administrator identities for authentication.
table user {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text name filters=trim
    email email filters=trim|lower
    password password filters=min:8|minAlpha:1|minDigit:1 {
      visibility = "internal"
    }
  
    text phone? filters=trim {
      visibility = "private"
    }
  
    // Clients have no company; administrators must be linked to exactly one.
    int account_id? {
      table = "account"
    }
  
    enum role {
      values = ["client", "admin"]
      visibility = "private"
    }
  
    object password_reset? {
      schema {
        password token? {
          visibility = "internal"
        }
      
        timestamp? expiration? {
          visibility = "internal"
        }
      
        bool used? {
          visibility = "internal"
        }
      }
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "g8tpjso2orFaPgdxKGzuuR66M1k"
}