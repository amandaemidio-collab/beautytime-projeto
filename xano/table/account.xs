// Stores company information for company administrators.
table account {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // The company's public name and booking-link identifier.
    text name filters=trim
    text public_identifier filters=trim
  
    // A brief description of the company.
    text description? filters=trim
  
    text location? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "gin", field: [{name: "xdo", op: "jsonb_path_op"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "public_identifier", op: "asc"}]}
  ]

  tags = ["xano:quick-start"]
  guid = "ny8yWAEDvYG_siNE6ohJbNk3Cqw"
}